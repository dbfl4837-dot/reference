import json

ANALYSIS_SYSTEM_INSTRUCTION = (
    "당신은 퍼포먼스 광고 전문 크리에이티브 전략가입니다. "
    "광고 레퍼런스를 상세히 분해하는 동시에, 구매 전환을 만든 '심리 구조'와 '설계 원리'를 깊이 있게 추출해야 합니다.\n"
    "우리 제품 정보는 절대 먼저 언급하지 마세요.\n\n"
    "[특별 지시사항]\n"
    "1. raw_script 항목에는 영상의 모든 음성과 핵심 텍스트를 타임라인이나 자막 표시 없이, 하나의 자연스러운 문단(줄글)으로 쭉 이어서 작성하세요. 절대 '(중략)'이나 요약을 하지 마세요.\n"
    "2. scene_analysis 항목은 영상이 있을 경우, 영상을 구간별(타임스탬프)로 나누어 장면별로 세밀하게 분석하세요."
)

ANALYSIS_JSON_SCHEMA_HINT = """
{
  "raw_script": "대본 전문 (타임라인/자막 표시 없이 화자의 대사만 쭉 이어진 줄글 형태. 복붙용)",
  "scene_analysis": [
    {
      "timestamp": "00:00 - 00:04",
      "ad_content": "광고 내용 분석",
      "consumer_psychology": "소비자 심리 분석",
      "conversion_role": "전환 역할 (예: Hook, Problem 등)",
      "core_message": "핵심 메시지/카피",
      "application_method": "타 제품 적용 방식"
    }
  ],
  "strategy_analysis": {
    "target_audience": "타깃 고객 분석",
    "customer_pain": "고객의 기존 고민",
    "category_inconvenience": "카테고리의 대표적인 불편",
    "negative_perception": "기존 제품에 대한 부정적 인식",
    "hesitation_reason": "구매를 망설이는 이유",
    "barrier_removed": "이 광고가 제거하려는 장벽",
    "positioning": "경쟁 제품과 다른 포지셔닝",
    "core_strategy": "광고 전략 핵심"
  },
  "hook_analysis": {
    "type": "Hook 유형",
    "sentence": "Hook 문장",
    "reason_chosen": "첫 문장/장면이 선택된 이유",
    "first_3s_psychology": "첫 3초에 자극하는 소비자 심리",
    "scroll_stop_reason": "시청자가 멈출 가능성이 높은 이유",
    "hook_formula": "사용된 후킹 공식",
    "conversion_impact": "구매 전환에 미치는 영향"
  },
  "structure_analysis": {
    "stages": [
      {"stage": "Hook/Problem/Solution/Proof/CTA 중 하나 기입", "ad_content": "광고 내용 분석", "consumer_psychology": "소비자 심리 분석", "conversion_role": "전환 역할"}
    ],
    "why_this_order": "왜 이 순서로 배치했는가 상세 분석",
    "visual_direction": "영상 연출 포인트 분석"
  },
  "psychology_analysis": [
    {"element": "분석 요소 (예: Pain Point 자극 방식, Desire 생성 등)", "usage": "광고 속 사용 방식", "psychology": "자극된 소비자 심리", "contribution": "전환 기여 이유"}
  ],
  "success_formula": {
    "why_it_works": "이 광고가 성과가 날 가능성이 높은 이유 종합",
    "formula_name": "반복 활용 가능한 공식명 창작",
    "formula_structure": "광고 구조 (예: 결과 제시 -> 문제 공감 -> 해결책...)",
    "suitable_situation": "적합한 상황",
    "core_psychology": "핵심 심리",
    "how_to_use": "해당 공식을 타 기획에 활용하는 방법"
  }
}
"""

PLAN_SYSTEM_INSTRUCTION = (
    "분석된 레퍼런스의 '성공 구매 심리 구조'를 바탕으로 우리 브랜드에 맞게 재해석한 고전환 광고 기획안을 작성합니다.\n"
    "우리 제품에 적용할 때는 원본 레퍼런스 광고의 뼈대와 전개 방식을 적극적으로 디벨롭하되, 우리 제품의 상세 정보를 자연스럽게 녹여내고 단정적 표현(심의 리스크)은 철저히 배제하세요.\n\n"
    "[절대 준수 사항]\n"
    "1. 'step6_ad_formulas' (고전환 공식)는 최소 3개 이상 반드시 작성하세요.\n"
    "2. 'step7_new_scripts' (신규 대본)는 원본 레퍼런스 대본을 기반으로 디벨롭하여, **30-40초 분량의 상세한 '풀버전 대본'을 정확히 5개** 작성하세요. 요약이나 중략 없이 시작부터 끝(CTA)까지 대사가 꽉 채워져 있어야 합니다.\n"
    "3. 'step8_cheat_keys' (치트키 워딩 리스트)는 카테고리별로 **반드시 5개 이상의 추천 워딩**을 꽉꽉 채워 작성하세요.\n"
    "4. 'step9_final_priority' (최종 우선순위)는 반드시 1순위, 2순위, 3순위까지 총 3개를 작성해야 합니다."
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
      "concept": "컨셉명 (레퍼런스 기반 디벨롭 방향)",
      "screen_composition": "화면 구성 및 연출 디렉션 (상세히)",
      "dialogue": "전체 대사 전문 (30-40초 분량, 도입부부터 마무리까지 빈틈없이 꽉 채운 풀버전)",
      "subtitle": "영상에 들어갈 핵심 강조 자막",
      "cta": "마지막 구매 유도 CTA 멘트 및 화면"
    }
  ],
  "step8_cheat_keys": [
    {"category": "후킹", "wording": "워딩1 / 워딩2 / 워딩3 / 워딩4 / 워딩5"},
    {"category": "고객 고민 자극", "wording": "워딩1 / 워딩2 / 워딩3 / 워딩4 / 워딩5"},
    {"category": "제품 신뢰", "wording": "워딩1 / 워딩2 / 워딩3 / 워딩4 / 워딩5"},
    {"category": "구매 유도", "wording": "워딩1 / 워딩2 / 워딩3 / 워딩4 / 워딩5"}
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
        f"[분석 요약]\n{analysis_summary}", f"[브랜드 및 제품명] {product_name}", f"[USP 및 추가 정보] {product_usp_notes}"
    ]
    if landing_url:
        parts.append(f"[제품 랜딩페이지 URL] {landing_url} (이 URL의 내용도 참고하여 제품의 타겟과 소구점을 반영해 주세요.)")
    parts.append("[만약 제품 상세페이지 이미지가 첨부되었다면, 이를 꼼꼼히 분석하여 기획에 핵심 소구점으로 반영하세요.]")
    parts.append(f"{PLAN_JSON_SCHEMA_HINT}")
    return "\n".join(parts)

def summarize_analysis_for_plan(analysis: dict) -> str:
    return json.dumps(analysis, ensure_ascii=False)[:3000]
