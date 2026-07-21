import os
import uuid
import html
import json
from datetime import timezone, timedelta
import pandas as pd
import streamlit as st
import database as db
import gemini
import prompts

st.set_page_config(page_title="Creative PRD", page_icon="🎯", layout="wide")
db.init_db()

KST = timezone(timedelta(hours=9))

def to_kst_str(dt, fmt="%Y-%m-%d %H:%M"):
    if dt is None:
        return ""
    return dt.replace(tzinfo=timezone.utc).astimezone(KST).strftime(fmt)

def render_table(df: pd.DataFrame):
    thead = "".join(f"<th>{html.escape(str(col))}</th>" for col in df.columns)
    rows = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td>{html.escape(str(val))}</td>" for val in row)
        rows += f"<tr>{cells}</tr>"
    table_html = f"""
    <div class="custom-table-wrap">
        <table class="custom-table">
            <thead><tr>{thead}</tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    button[kind="primary"] { background-color: #007AFF !important; color: white !important; border: none !important; border-radius: 8px !important; }
    button[kind="primary"]:hover { background-color: #005bb5 !important; }
    *:focus { outline: none !important; box-shadow: none !important; border-color: transparent !important; }
    div[data-baseweb="select"] > div:focus-within { box-shadow: 0 0 0 1px #007AFF !important; border-color: #007AFF !important; }
    hr { border-color: #E5E5EA !important; margin: 2rem 0; }
    .custom-table-wrap { width: 100%; overflow-x: auto; margin-bottom: 1rem; border: 1px solid #E5E5EA; border-radius: 8px; padding-bottom: 0; }
    .custom-table { border-collapse: collapse; width: max-content; min-width: 100%; margin-bottom: 0; }
    .custom-table-wrap::-webkit-scrollbar { height: 6px; }
    .custom-table-wrap::-webkit-scrollbar-thumb { background-color: #C7C7CC; border-radius: 3px; }
    .custom-table-wrap::-webkit-scrollbar-track { background-color: transparent; }
    .custom-table th { background-color: #EAEAEA; color: #1C1C1E; font-weight: 600; font-size: 0.95rem; text-align: left; padding: 12px; border-bottom: 2px solid #D1D1D6; white-space: nowrap; }
    .custom-table td { padding: 12px; border-bottom: 1px solid #E5E5EA; color: #3A3A3C; font-size: 0.9rem; line-height: 1.5; white-space: nowrap; }
    div[data-testid="stContainer"] { border-color: #E5E5EA !important; border-radius: 12px !important; padding: 1rem !important; }
    
    /* 타임라인 박스 스타일 추가 */
    .timeline-box {
        border: 1px solid #E5E5EA;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        background-color: #FAFAFC;
    }
    .timeline-time {
        font-weight: 700;
        color: #007AFF;
        margin-bottom: 12px;
        font-size: 1.1rem;
    }
    .timeline-item {
        margin-bottom: 8px;
        font-size: 0.95rem;
    }
    .timeline-item strong {
        color: #1C1C1E;
        display: inline-block;
        width: 130px;
    }
    </style>
""", unsafe_allow_html=True)

def render_analysis_report(res: dict):
    st.markdown("#### 📺 원본 광고 대본 전문")
    st.info("우측 상단의 복사 아이콘을 클릭하여 기획안에 바로 붙여넣으세요.")
    st.code(res.get("raw_script", ""), language="text")

    st.markdown("#### 1. 영상별 전수 분석 (구조적 분해)")
    if res.get("step1_full_analysis"):
        df1 = pd.DataFrame(res["step1_full_analysis"])
        df1.columns = ["항목", "상세 분석"]
        render_table(df1)
        
    # === 새로 추가된 부분: 2. 장면별 광고 분석 ===
    if res.get("step1_5_scene_analysis"):
        st.markdown("#### 2. 장면별 광고 분석")
        for scene in res["step1_5_scene_analysis"]:
            html_content = f"""
            <div class="timeline-box">
                <div class="timeline-time">{html.escape(scene.get('timestamp', ''))}</div>
                <div class="timeline-item"><strong>광고 내용</strong> : {html.escape(scene.get('ad_content', ''))}</div>
                <div class="timeline-item"><strong>소비자 심리</strong> : {html.escape(scene.get('consumer_psychology', ''))}</div>
                <div class="timeline-item"><strong>전환 역할</strong> : {html.escape(scene.get('conversion_role', ''))}</div>
                <div class="timeline-item"><strong>핵심 메시지</strong> : {html.escape(scene.get('core_message', ''))}</div>
                <div class="timeline-item"><strong>타 제품 적용 방식</strong> : {html.escape(scene.get('application_method', ''))}</div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)

    st.markdown("#### 3. 경쟁사 광고 승리 패턴 추출")
    if res.get("step2_winning_pattern"):
        df2 = pd.DataFrame(res["step2_winning_pattern"])
        df2.rename(columns={"pattern": "승리 패턴", "sentence_structure": "사용된 문장 구조", "psychology": "자극한 고객 심리", "application": "적용 방식"}, inplace=True)
        render_table(df2)

    st.markdown("#### 4. HOOK-BODY-ACTION 구조 분해")
    hba = res.get("step3_hba_structure", {}) or {}
    st.markdown(f"**HOOK (0~3초):** {hba.get('hook', '')}")
    st.markdown("**BODY (4~12초):**")
    st.markdown(f"- 문제: {hba.get('body_problem', '')}")
    st.markdown(f"- 해결: {hba.get('body_solution', '')}")
    st.markdown(f"- 증거: {hba.get('body_proof', '')}")
    st.markdown(f"**ACTION (13~15초):** {hba.get('action', '')}")

    st.markdown("#### 5. 핵심 구매 심리 분석")
    beh = res.get("step4_behavioral_psychology", {}) or {}
    st.markdown(f"- **타깃 고객 문제/감정:** {beh.get('target_problem_emotion', '')}")
    st.markdown(f"- **구매 욕구를 만든 핵심 심리:** {beh.get('core_psychology', '')}")
    with st.container():
        st.success(f"💡 **왜 사용자가 멈추고 구매하는가:** {beh.get('why_it_works', '')}")


def render_plan_report(plan: dict):
    st.markdown("#### 6. 우리 브랜드 적용 방향")
    bd = plan.get("step5_brand_direction", {}) or {}
    st.markdown(f"- **심리 구조 유지 방안:** {bd.get('psychology_match', '')}")
    st.markdown(f"- **우리 고객의 실제 고민:** {bd.get('customer_worry', '')}")
    st.markdown(f"- **카테고리 상황 설정:** {bd.get('category_situation', '')}")
    st.warning(f"🚨 **심의 리스크 회피:** {bd.get('risk_management', '')}")

    st.markdown("#### 7. 우리 브랜드용 고전환 광고 공식")
    if plan.get("step6_ad_formulas"):
        df_form = pd.DataFrame(plan["step6_ad_formulas"])
        df_form.rename(columns={"formula_name": "공식명", "core_psychology": "핵심 심리", "suitable_situation": "적합 상황", "hook_example": "Hook 예시", "script_flow": "대본 전개", "required_screen": "필수 화면", "cta_method": "CTA 방식"}, inplace=True)
        render_table(df_form)

    st.markdown("#### 8. 신규 광고 대본 제작 (예시)")
    if plan.get("step7_new_scripts"):
        df_scripts = pd.DataFrame(plan["step7_new_scripts"])
        df_scripts.rename(columns={"concept": "컨셉명", "screen_composition": "화면 구성", "dialogue": "대사", "subtitle": "자막", "cta": "CTA"}, inplace=True)
        render_table(df_scripts)

    st.markdown("#### 9. 치트키 워딩 리스트")
    if plan.get("step8_cheat_keys"):
        df_cheat = pd.DataFrame(plan["step8_cheat_keys"])
        df_cheat.rename(columns={"category": "카테고리", "wording": "워딩"}, inplace=True)
        render_table(df_cheat)

    st.markdown("#### 10. 🎯 최종 우선순위 (제작 가이드)")
    for prio in plan.get("step9_final_priority", []) or []:
        st.markdown(f"**{prio.get('priority', '')}:** {prio.get('reason', '')}")


def _load_analysis_dict(analysis) -> dict | None:
    if not analysis: return None
    def _parse(raw, default):
        if not raw: return default
        try: return json.loads(raw)
        except (TypeError, ValueError): return default
    return {
        "raw_script": analysis.raw_script or "",
        "step1_full_analysis": _parse(analysis.step1_full_analysis, []),
        "step1_5_scene_analysis": _parse(analysis.step1_5_scene_analysis, []), # 추가된 부분
        "step2_winning_pattern": _parse(analysis.step2_winning_pattern, []),
        "step3_hba_structure": _parse(analysis.step3_hba_structure, {}),
        "step4_behavioral_psychology": _parse(analysis.step4_behavioral_psychology, {}),
    }


def _load_plan_dict(plan) -> dict | None:
    if not plan: return None
    def _parse(raw, default):
        if not raw: return default
        try: return json.loads(raw)
        except (TypeError, ValueError): return default
    return {
        "step5_brand_direction": _parse(plan.step5_brand_direction, {}),
        "step6_ad_formulas": _parse(plan.step6_ad_formulas, []),
        "step7_new_scripts": _parse(plan.step7_new_scripts, []),
        "step8_cheat_keys": _parse(plan.step8_cheat_keys, []),
        "step9_final_priority": _parse(plan.step9_final_priority, []),
    }

if "page" not in st.session_state: st.session_state["page"] = "Home"

def render_nav():
    cols = st.columns([1, 1, 1, 1, 6])
    pages = ["Home", "Library", "Settings"]
    for col, page in zip(cols, pages):
        with col:
            if st.button(page, use_container_width=True, type="primary" if st.session_state["page"] == page else "secondary"):
                st.session_state["page"] = page
                st.rerun()
    st.divider()

def render_home():
    st.markdown("### 📁 1. 프로젝트 / 제품")
    projects = {p.id: p.name for p in db.list_projects()}
    
    c1, c2 = st.columns([5, 1], vertical_alignment="bottom")
    with c1:
        proj_id = st.selectbox("프로젝트 선택", options=[None] + list(projects.keys()), format_func=lambda x: projects.get(x, "선택 안 함"))
        st.session_state["selected_project_id"] = proj_id
    with c2:
        with st.popover("+ 새 프로젝트", use_container_width=True):
            new_p = st.text_input("프로젝트명")
            if st.button("생성", use_container_width=True): db.create_project(new_p); st.rerun()
                
    if proj_id:
        products = {p.id: p.name for p in db.list_products(proj_id)}
        c3, c4 = st.columns([5, 1], vertical_alignment="bottom")
        with c3:
            prod_id = st.selectbox("제품 선택 (적용 단계에만 사용)", options=[None] + list(products.keys()), format_func=lambda x: products.get(x, "선택 안 함"))
            st.session_state["selected_product_id"] = prod_id
        with c4:
            with st.popover("+ 새 제품", use_container_width=True):
                new_prod = st.text_input("제품명")
                new_url = st.text_input("랜딩페이지 URL (선택)")
                new_imgs = st.file_uploader("상세페이지 캡쳐본 (선택)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
                
                if st.button("제품 생성", use_container_width=True):
                    img_paths_json = ""
                    if new_imgs:
                        saved_paths = []
                        for img in new_imgs:
                            ext = os.path.splitext(img.name)[1]
                            path = os.path.join("data", "uploads", f"{uuid.uuid4().hex}{ext}")
                            os.makedirs(os.path.dirname(path), exist_ok=True)
                            with open(path, "wb") as f:
                                f.write(img.getbuffer())
                            saved_paths.append(path)
                        img_paths_json = json.dumps(saved_paths)

                    db.create_product(proj_id, new_prod, "", landing_url=new_url, image_paths=img_paths_json)
                    st.rerun()

    st.divider()
    st.markdown("### 🎬 2. 광고 영상 업로드")
    videos = st.file_uploader("분석할 광고 영상을 업로드해주세요.", type=["mp4", "mov"], accept_multiple_files=True)
    
    st.write("") 
    
    if st.button("🔍 광고 레퍼런스 심층 분석", type="primary", use_container_width=True):
        if not videos: 
            return st.warning("영상을 업로드해주세요.")
        with st.spinner("광고 레퍼런스의 심리 구조와 타임라인을 분석하고 있습니다..."):
            v_path = None
            if videos:
                ext = os.path.splitext(videos[0].name)[1]
                v_path = os.path.join("data", "tmp", f"temp_{uuid.uuid4().hex}{ext}")
                os.makedirs(os.path.dirname(v_path), exist_ok=True)
                with open(v_path, "wb") as f: f.write(videos[0].getbuffer())
                st.session_state["last_video_name"] = videos[0].name
            try:
                res, _ = gemini.analyze_reference("", v_path)
                st.session_state["analysis_res"] = res
                st.session_state["plan_res"] = None
            except Exception as e: st.error(str(e))
            finally:
                if v_path and os.path.exists(v_path):
                    try: os.remove(v_path)
                    except OSError: pass
                
    res = st.session_state.get("analysis_res")
    if res:
        st.markdown("---")
        st.subheader("📊 광고 레퍼런스 심층 분석")
        render_analysis_report(res)

        st.markdown("---")
        if st.button("✨ 우리 브랜드 적용 기획안 생성", type="primary"):
            p = db.get_product(st.session_state.get("selected_product_id"))
            if not p: return st.warning("적용할 '제품'을 상단에서 먼저 선택해 주세요.")
            with st.spinner("제품의 상세 정보와 캡처 이미지를 바탕으로 우리 제품 맞춤형 신규 대본을 생성 중입니다..."):
                img_paths = []
                if p.image_paths:
                    try: img_paths = json.loads(p.image_paths)
                    except: pass
                    
                plan, _ = gemini.generate_plan(
                    analysis_summary=prompts.summarize_analysis_for_plan(res), 
                    product_name=p.name, 
                    product_usp_notes=p.usp_notes or "",
                    landing_url=p.landing_url or "",
                    image_paths=img_paths
                )
                st.session_state["plan_res"] = plan
                    
        plan = st.session_state.get("plan_res")
        if plan:
            st.subheader("🎯 우리 브랜드 적용")
            render_plan_report(plan)

            st.write("")
            if st.button("💾 이 기획안 최종 저장", type="primary", use_container_width=True):
                r = db.create_reference(
                    project_id=st.session_state["selected_project_id"],
                    product_id=st.session_state["selected_product_id"],
                    ad_copy_text="",
                    video_paths=st.session_state.get("last_video_name", ""),
                )
                res["raw_script"] = res.get("raw_script")
                db.save_analysis(r.id, res)
                db.save_plan(r.id, plan)
                st.success("데이터베이스에 성공적으로 저장되었습니다.")

def render_library():
    st.markdown("### 📚 Library (저장된 기획안)")
    projects = {p.id: p.name for p in db.list_projects()}
    
    c1, c2 = st.columns(2)
    with c1:
        proj_filter = st.selectbox("프로젝트 필터", options=[None] + list(projects.keys()), format_func=lambda x: "전체보기" if x is None else projects[x])
    with c2:
        products = {p.id: p.name for p in db.list_products(proj_filter)} if proj_filter else {}
        prod_filter = st.selectbox("제품 필터", options=[None] + list(products.keys()), format_func=lambda x: "전체보기" if x is None else products[x])
        
    refs = db.search_references(project_id=proj_filter, product_id=prod_filter)
    st.caption(f"총 {len(refs)}건의 저장된 데이터가 있습니다.")
    
    for ref in refs:
        default_title = f"{ref.video_paths or '이름 없는 기획안'} · {to_kst_str(ref.created_at)}"
        display_title = ref.ad_copy_text.strip() if ref.ad_copy_text and ref.ad_copy_text.strip() else default_title

        with st.expander(f"🎬 {display_title}"):
            c1, c2 = st.columns([5, 1], vertical_alignment="bottom")
            with c1:
                new_title = st.text_input(
                    "이름 수정",
                    value=ref.ad_copy_text if ref.ad_copy_text else "",
                    placeholder=default_title,
                    key=f"title_input_{ref.id}",
                )
            with c2:
                if st.button("이름 저장", key=f"save_title_{ref.id}", use_container_width=True):
                    db.update_reference_title(ref.id, new_title)
                    st.rerun()
            st.caption(f"기본 이름: {default_title} (수정하지 않으면 이 이름으로 표시돼요)")
            st.divider()

            res = _load_analysis_dict(ref.analysis)
            plan = _load_plan_dict(ref.plan)

            if res:
                st.subheader("📊 광고 레퍼런스 심층 분석")
                render_analysis_report(res)

            if plan:
                st.markdown("---")
                st.subheader("🎯 우리 브랜드 적용")
                render_plan_report(plan)

            if not res and not plan:
                st.write("저장된 분석 데이터가 없습니다.")

            st.write("")
            if st.button("🗑 이 기획안 삭제", key=f"del_ref_{ref.id}"):
                db.delete_reference(ref.id)
                st.rerun()

render_nav()
if st.session_state["page"] == "Home": render_home()
elif st.session_state["page"] == "Library": render_library()
elif st.session_state["page"] == "Settings":
    st.markdown("### ⚙️ Settings - 제품 관리")
    for proj in db.list_projects():
        with st.expander(f"{proj.name}"):
            for prod in db.list_products(proj.id):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{prod.name}**")
                if c2.button("🗑 삭제", key=f"del_{prod.id}"):
                    db.delete_product(prod.id)
                    st.rerun()