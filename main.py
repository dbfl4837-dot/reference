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
    if dt is None: return ""
    return dt.replace(tzinfo=timezone.utc).astimezone(KST).strftime(fmt)

st.markdown("""
    <style>
    .stApp { background-color: #F9FAFB; }
    button[kind="primary"] { background-color: #007AFF !important; color: white !important; border: none !important; border-radius: 8px !important; }
    button[kind="primary"]:hover { background-color: #005bb5 !important; }
    *:focus { outline: none !important; box-shadow: none !important; border-color: transparent !important; }
    div[data-baseweb="select"] > div:focus-within { box-shadow: 0 0 0 1px #007AFF !important; border-color: #007AFF !important; }
    hr { border-color: #E5E5EA !important; margin: 2rem 0; }
    
    /* 완벽하게 살아난 깔끔한 카드 스타일 */
    div[data-testid="stContainer"] { 
        background-color: #FFFFFF !important; 
        border: 1px solid #E5E5EA !important; 
        border-radius: 12px !important; 
        padding: 1.5rem !important; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
        margin-bottom: 1.2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

def render_analysis_report(res: dict):
    st.markdown("#### 📺 원본 광고 대본 전문")
    st.info("우측 상단의 복사 아이콘을 클릭하여 기획안에 바로 붙여넣으세요.")
    
    raw_script_text = res.get("raw_script", "")
    if raw_script_text:
        with st.container():
            st.markdown(raw_script_text)

    if res.get("scene_analysis"):
        st.markdown("#### 1. 장면별 광고 분석")
        for scene in res["scene_analysis"]:
            with st.container():
                st.markdown(f"**⏱ {scene.get('timestamp', '')}**")
                st.markdown(f"• **광고 내용:** {scene.get('ad_content', '')}")
                st.markdown(f"• **소비자 심리:** {scene.get('consumer_psychology', '')}")
                st.markdown(f"• **전환 역할:** {scene.get('conversion_role', '')}")
                st.markdown(f"• **핵심 메시지:** {scene.get('core_message', '')}")
                st.markdown(f"• **타 제품 적용 방식:** {scene.get('application_method', '')}")

    strat = res.get("strategy_analysis", {})
    if strat:
        st.markdown("#### 2. 광고 전략 분석")
        with st.container():
            st.markdown(f"• **타깃 고객:** {strat.get('target_audience', '')}")
            st.markdown(f"• **고객의 기존 고민:** {strat.get('customer_pain', '')}")
            st.markdown(f"• **카테고리 불편:** {strat.get('category_inconvenience', '')}")
            st.markdown(f"• **부정적 인식:** {strat.get('negative_perception', '')}")
            st.markdown(f"• **구매 망설임 이유:** {strat.get('hesitation_reason', '')}")
            st.markdown(f"• **제거한 진입장벽:** {strat.get('barrier_removed', '')}")
            st.markdown(f"• **차별화 포지셔닝:** {strat.get('positioning', '')}")
            st.info(f"💡 **광고 전략 핵심:** {strat.get('core_strategy', '')}")

    hook = res.get("hook_analysis", {})
    if hook:
        st.markdown("#### 3. Hook 상세 분석")
        with st.container():
            st.markdown(f"• **Hook 유형:** {hook.get('type', '')}")
            st.markdown(f"• **Hook 문장:** {hook.get('sentence', '')}")
            st.markdown(f"• **첫 문장/장면 선택 이유:** {hook.get('reason_chosen', '')}")
            st.markdown(f"• **첫 3초 자극 심리:** {hook.get('first_3s_psychology', '')}")
            st.markdown(f"• **시청 지속 이유:** {hook.get('scroll_stop_reason', '')}")
            st.markdown(f"• **사용된 공식:** {hook.get('hook_formula', '')}")
            st.markdown(f"• **전환 미치는 영향:** {hook.get('conversion_impact', '')}")

    struct = res.get("structure_analysis", {})
    if struct:
        st.markdown("#### 4. 광고 구조 분해")
        stages = struct.get("stages", [])
        for stage in stages:
            with st.container():
                st.markdown(f"**📌 단계: {stage.get('stage', '')}**")
                st.markdown(f"• **광고 내용:** {stage.get('ad_content', '')}")
                st.markdown(f"• **소비자 심리:** {stage.get('consumer_psychology', '')}")
                st.markdown(f"• **전환 역할:** {stage.get('conversion_role', '')}")
        st.info(f"📍 **왜 이 순서로 배치했는가:** {struct.get('why_this_order', '')}")
        st.info(f"🎬 **영상 연출 포인트:** {struct.get('visual_direction', '')}")

    psych = res.get("psychology_analysis", [])
    if psych:
        st.markdown("#### 5. 구매 심리 분석")
        for item in psych:
            with st.container():
                st.markdown(f"**🔹 {item.get('element', '')}**")
                st.markdown(f"• **사용 방식:** {item.get('usage', '')}")
                st.markdown(f"• **소비자 심리:** {item.get('psychology', '')}")
                st.markdown(f"• **전환 기여 이유:** {item.get('contribution', '')}")

    formula = res.get("success_formula", {})
    if formula:
        st.markdown("#### 6. 반복 활용 가능한 성공 공식 추출")
        st.success(f"**📈 이 광고가 성과가 날 가능성이 높은 이유:**\n{formula.get('why_it_works', '')}")
        with st.container():
            st.markdown(f"**🏆 공식명:** {formula.get('formula_name', '')}")
            st.markdown(f"• **광고 구조:** {formula.get('formula_structure', '')}")
            st.markdown(f"• **적합한 상황:** {formula.get('suitable_situation', '')}")
            st.markdown(f"• **핵심 심리:** {formula.get('core_psychology', '')}")
            st.markdown(f"• **활용 방법:** {formula.get('how_to_use', '')}")

def render_plan_report(plan: dict):
    st.markdown("#### 👉 1. 우리 브랜드 적용 방향")
    bd = plan.get("step5_brand_direction", {}) or {}
    with st.container():
        st.markdown(f"• **심리 구조 유지 방안:** {bd.get('psychology_match', '')}")
        st.markdown(f"• **우리 고객의 실제 고민:** {bd.get('customer_worry', '')}")
        st.markdown(f"• **카테고리 상황 설정:** {bd.get('category_situation', '')}")
        st.warning(f"🚨 **심의 리스크 회피:** {bd.get('risk_management', '')}")

    st.markdown("#### 👉 2. 우리 브랜드용 고전환 광고 공식")
    formulas = plan.get("step6_ad_formulas", [])
    for f in formulas:
        with st.container():
            st.markdown(f"**📌 공식명: {f.get('formula_name', '')}**")
            st.markdown(f"• **핵심 심리:** {f.get('core_psychology', '')}")
            st.markdown(f"• **적합 상황:** {f.get('suitable_situation', '')}")
            st.markdown(f"• **Hook 예시:** {f.get('hook_example', '')}")
            st.markdown(f"• **대본 전개:** {f.get('script_flow', '')}")
            st.markdown(f"• **필수 화면:** {f.get('required_screen', '')}")
            st.markdown(f"• **CTA 방식:** {f.get('cta_method', '')}")

    st.markdown("#### 👉 3. 신규 광고 대본 (풀버전 5종)")
    scripts = plan.get("step7_new_scripts", [])
    for s in scripts:
        with st.container():
            st.markdown(f"### 🎬 컨셉명: {s.get('concept', '')}")
            st.markdown("**화면 구성:**")
            st.caption(s.get('screen_composition', ''))
            st.markdown("**대사 (전문):**")
            st.code(s.get('dialogue', ''), language="text")
            st.markdown(f"• **자막:** {s.get('subtitle', '')}")
            st.markdown(f"• **CTA:** {s.get('cta', '')}")

    st.markdown("#### 👉 4. 치트키 워딩 리스트")
    cheats = plan.get("step8_cheat_keys", [])
    if cheats:
        for c in cheats:
            with st.container():
                st.markdown(f"**🏷️ {c.get('category', '기타')}**")
                raw_words = c.get('wording', '')
                words = [w.strip() for w in raw_words.replace('/', ',').split(',') if w.strip()]
                for w in words:
                    st.markdown(f"• {w}")

    st.markdown("#### 👉 5. 🎯 최종 우선순위 (제작 가이드)")
    for prio in plan.get("step9_final_priority", []) or []:
        st.info(f"**{prio.get('priority', '')}:** {prio.get('reason', '')}")

def _load_analysis_dict(analysis) -> dict | None:
    if not analysis: return None
    def _parse(raw, default):
        if not raw: return default
        try: return json.loads(raw)
        except (TypeError, ValueError): return default
    return {
        "raw_script": analysis.raw_script or "",
        "scene_analysis": _parse(analysis.scene_analysis, []),
        "strategy_analysis": _parse(analysis.strategy_analysis, {}),
        "hook_analysis": _parse(analysis.hook_analysis, {}),
        "structure_analysis": _parse(analysis.structure_analysis, {}),
        "psychology_analysis": _parse(analysis.psychology_analysis, []),
        "success_formula": _parse(analysis.success_formula, {}),
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

@st.dialog("📁 새 브랜드 만들기")
def create_project_dialog():
    new_p = st.text_input("브랜드명")
    if st.button("생성하기", type="primary", use_container_width=True):
        if not new_p.strip(): st.warning("브랜드명을 입력해주세요.")
        else:
            with st.spinner("로딩 중..."): db.create_project(new_p)
            st.toast(f"✅ 브랜드 '{new_p}' 생성 완료!")
            st.rerun()

@st.dialog("📦 새 제품 추가하기")
def create_product_dialog(proj_id):
    new_prod = st.text_input("제품명")
    new_url = st.text_input("랜딩페이지 URL (선택)")
    new_imgs = st.file_uploader("상세페이지 캡쳐본 (선택)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    if st.button("제품 생성하기", type="primary", use_container_width=True):
        if not new_prod.strip(): st.warning("제품명을 입력해주세요.")
        else:
            with st.spinner("로딩 중..."):
                img_paths_json = ""
                if new_imgs:
                    saved_paths = []
                    for img in new_imgs:
                        ext = os.path.splitext(img.name)[1]
                        path = os.path.join("data", "uploads", f"{uuid.uuid4().hex}{ext}")
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        with open(path, "wb") as f: f.write(img.getbuffer())
                        saved_paths.append(path)
                    img_paths_json = json.dumps(saved_paths)
                db.create_product(proj_id, new_prod, "", landing_url=new_url, image_paths=img_paths_json)
            st.toast(f"✅ 제품 '{new_prod}' 생성 완료!")
            st.rerun()

def render_home():
    st.markdown("### 📁 1. 브랜드 / 제품")
    projects = {p.id: p.name for p in db.list_projects()}
    
    c1, c2 = st.columns([5, 1], vertical_alignment="bottom")
    with c1:
        proj_options = list(projects.keys())
        proj_id = st.selectbox("브랜드 선택", options=proj_options, format_func=lambda x: projects.get(x, ""))
        st.session_state["selected_project_id"] = proj_id
    with c2:
        if st.button("+ 새 브랜드", use_container_width=True): create_project_dialog()
                
    if proj_id:
        products = {p.id: p.name for p in db.list_products(proj_id)}
        c3, c4 = st.columns([5, 1], vertical_alignment="bottom")
        with c3:
            prod_options = list(products.keys())
            prod_id = st.selectbox("제품 선택", options=prod_options, format_func=lambda x: products.get(x, ""))
            st.session_state["selected_product_id"] = prod_id
        with c4:
            if st.button("+ 새 제품", use_container_width=True): create_product_dialog(proj_id)

    st.divider()
    st.markdown("### 🎬 2. 광고 영상 업로드")
    videos = st.file_uploader("분석할 광고 영상을 업로드해주세요.", type=["mp4", "mov"], accept_multiple_files=True)
    
    st.write("") 
    if st.button("🔍 광고 레퍼런스 심층 분석", type="primary", use_container_width=True):
        if not videos: return st.warning("영상을 업로드해주세요.")
        with st.spinner("로딩 중..."):
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
            except Exception as e: 
                st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
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
            
            with st.spinner("로딩 중..."):
                img_paths = []
                if p.image_paths:
                    try: img_paths = json.loads(p.image_paths)
                    except: pass
                    
                try:
                    plan, _ = gemini.generate_plan(
                        analysis_summary=prompts.summarize_analysis_for_plan(res), 
                        product_name=p.name, 
                        product_usp_notes=p.usp_notes or "",
                        landing_url=p.landing_url or "",
                        image_paths=img_paths
                    )
                    st.session_state["plan_res"] = plan
                except Exception as e:
                    st.error(f"기획안 생성 중 오류가 발생했습니다: {str(e)}")
                    
        plan = st.session_state.get("plan_res")
        if plan:
            st.subheader("🎯 우리 브랜드 적용 기획안")
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
        proj_filter = st.selectbox("브랜드 필터", options=[None] + list(projects.keys()), format_func=lambda x: "전체보기" if x is None else projects[x])
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
                new_title = st.text_input("이름 수정", value=ref.ad_copy_text if ref.ad_copy_text else "", placeholder=default_title, key=f"title_input_{ref.id}")
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
                st.subheader("🎯 우리 브랜드 적용 기획안")
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
