import json

ANALYSIS_SYSTEM_INSTRUCTION = (
    "당신은 퍼포먼스 광고 전문 크리에이티브 전략가입니다. "
    "광고 레퍼런스를 상세히 분해하는 동시에, 구매 전환을 만든 '심리 구조'와 '설계 원리'를 깊이 있게 추출해야 합니다.\n"
    "우리 제품 정보는 절대 먼저 언급하지 마세요.\n\n"
    "[특별 지시사항]\n"
    "1. raw_script 항목에는 영상의 모든 음성과 핵심 텍스트를 타임라인이나 자막 표시 없이, 하나의 자연스러운 문단(줄글)으로 쭉 이어서 작성하세요. 절대 '(중략)'이나 요약을 하지 마세요.\n"
    "2. step1_5_scene_analysis 항목은 영상이 있을 경우, 영상을 구간별(타임스탬프)로 나누어 장면별로 세밀하게 분석하세요."
)

ANALYSIS_JSON_SCHEMA_HINT = """
{
  "raw_script": "대본 전문 (타임라인/자막 표시 없이 화자의 대사만 쭉 이어진 줄글 형태. 복붙용)",
  "step1_full_analysis": [
    {"item": "첫 1초 후킹", "detail": "상세 분석 내용"},
    {"item": "초반 3초 HOOK", "detail": "이탈 방지 요소 및 상세 분석"},
    {"item": "핵심 문제 제기", "detail": "상세 분석 내용"},
    {"item": "핵심 소구", "detail": "USP 전달 방식 및 내용"},
    {"item": "신뢰 장치", "detail": "상세 분석 내용"},
    {"item": "혜택/마감", "detail": "구매 전환 장치(가격, 혜택 등)"},
    {"item": "CTA", "detail": "CTA 방식 상세"},
    {"item": "성과 예상 이유", "detail": "상세 분석 내용"}
  ],
  "step1_5_scene_analysis": [
    {
      "timestamp": "00:00~00:04",
      "ad_content": "광고 내용 분석",
      "consumer_psychology": "소비자 심리 분석",
      "conversion_role": "전환 역할 (예: Hook, Problem 등)",
      "core_message": "핵심 메시지/카피",
      "application_method": "타 제품 적용 방식"
    }
  ],
  "step2_winning_pattern": [
    {"pattern": "승리 패턴 (예: 역할극 네고)", "sentence_structure": "사용된 문장 구조", "psychology": "자극한 고객 심리", "application": "적용 방식"}
  ],
  "step3_hba_structure": {
    "hook": "HOOK (0~3초) 분석 내용",
    "body_problem": "BODY - 고객의 불편함/욕구/고민",
    "body_solution": "BODY - 문제 해결 기대감 제시 방식",
    "body_proof": "BODY - 증거 및 신뢰 요소",
    "action": "ACTION (13~15초) 구매 유도 마지막 장치"
  },
  "step4_behavioral_psychology": {
    "target_problem_emotion": "타깃 고객의 문제 상황 및 감정",
    "core_psychology": "구매 욕구를 만든 핵심 심리",
    "why_it_works": "단순히 '재밌다'가 아니라 행동 심리 관점에서 왜 멈추고 구매하는지 종합 분석"
  }
}
"""

PLAN_SYSTEM_INSTRUCTION = (
    "분석된 레퍼런스의 '성공 구매 심리 구조'를 바탕으로 우리 브랜드에 맞게 재해석한 고전환 광고 기획안을 작성합니다.\n"
    "우리 제품에 적용할 때는 레퍼런스 광고를 그대로 따라 하지 않고 동일한 심리 구조만 유지하며, 광고 심의 리스크가 있는 단정적 표현은 철저히 배제하세요.\n\n"
    "[절대 준수 사항]\n"
    "1. 'step6_ad_formulas' (고전환 공식)는 최소 3개 이상 반드시 작성하세요.\n"
    "2. 'step7_new_scripts' (신규 대본)는 제품 설명부터 시작하지 않고 자연스러운 대화형 구성으로 최소 5개를 작성하세요.\n"
    "3. 'step9_final_priority' (최종 우선순위)는 반드시 1순위, 2순위, 3순위까지 총 3개를 작성해야 합니다."
)

PLAN_JSON_SCHEMA_HINT = """
{
  "step5_brand_direction": {
    "psychology_match": "동일한 심리 구조 유지 방안",
    "customer_worry": "우리 제품 고객의 실제 고민 반영",
    "category_situation": "제품 카테고리에 맞는 상황 설정",
    "risk_management": "심의 리스크 회피 및 대체 표현 가이드"
  },
  "step6_ad_formulas": [
    {
      "formula_name": "공식명",
      "core_psychology": "핵심 심리 구조",
      "suitable_situation": "적합한 상황",
      "hook_example": "Hook 예시",
      "script_flow": "대본 전개 방식",
      "required_screen": "필수 화면 요소",
      "cta_method": "CTA 방식"
    }
  ],
  "step7_new_scripts": [
    {
      "concept": "컨셉명",
      "screen_composition": "화면 구성",
      "dialogue": "대사 (대화형)",
      "subtitle": "자막",
      "cta": "CTA"
    }
  ],
  "step8_cheat_keys": [
    {"category": "후킹", "wording": "짧은 문구"},
    {"category": "고객 고민 자극", "wording": "짧은 문구"},
    {"category": "제품 신뢰", "wording": "짧은 문구"},
    {"category": "구매 유도", "wording": "짧은 문구"}
  ],
  "step9_final_priority": [
    {"priority": "1순위 (예: 네고형)", "reason": "제작 추천 이유 상세 설명"},
    {"priority": "2순위 (예: 체감형)", "reason": "제작 추천 이유 상세 설명"},
    {"priority": "3순위 (예: 공감형)", "reason": "제작 추천 이유 상세 설명"}
  ]
}
"""

def build_analysis_prompt(ad_copy_text: str, has_video: bool = False) -> str:
    parts = ["퍼포먼스 광고 분석을 시작합니다. JSON으로만 응답하세요.", f"[광고 카피]\n{ad_copy_text}"]
    if has_video: parts.append("[영상 첨부됨]")
    parts.append(f"{ANALYSIS_JSON_SCHEMA_HINT}")
    return "\n".join(parts)

def build_plan_prompt(analysis_summary: str, product_name: str, product_usp_notes: str = "", landing_url: str = "") -> str:
    parts = [
        "위 분석을 우리 제품에 적용하여 기획안을 작성합니다. JSON으로만 응답하세요.",
        f"[분석 요약]\n{analysis_summary}", f"[제품명] {product_name}", f"[USP 및 추가 정보] {product_usp_notes}"
    ]
    if landing_url:
        parts.append(f"[제품 랜딩페이지 URL] {landing_url} (이 URL의 내용도 참고하여 제품의 타겟과 소구점을 반영해 주세요.)")
    parts.append("[만약 제품 상세페이지 이미지가 첨부되었다면, 이를 꼼꼼히 분석하여 기획에 핵심 소구점으로 반영하세요.]")
    parts.append(f"{PLAN_JSON_SCHEMA_HINT}")
    return "\n".join(parts)

def summarize_analysis_for_plan(analysis: dict) -> str:
    return json.dumps(analysis, ensure_ascii=False)[:3000]