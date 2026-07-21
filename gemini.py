from __future__ import annotations
import json
import os
import re
import time
from typing import Any, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import (
    ANALYSIS_SYSTEM_INSTRUCTION,
    PLAN_SYSTEM_INSTRUCTION,
    build_analysis_prompt,
    build_plan_prompt,
)

load_dotenv()

_DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
_DEFAULT_VIDEO_MODEL = os.getenv("GEMINI_VIDEO_MODEL", "gemini-3.1-flash-lite")

class GeminiError(Exception):
    pass

def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise GeminiError("GEMINI_API_KEY가 설정되어 있지 않습니다. .env 파일을 확인해주세요.")
    return api_key

def is_configured() -> bool:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return bool(api_key) and api_key != "your_gemini_api_key_here"

def _normalize_model(model_name: Optional[str], default: str) -> str:
    target_model = model_name or default
    if not target_model.startswith("models/"):
        target_model = f"models/{target_model}"
    return target_model

def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", cleaned, flags=re.MULTILINE).strip()
    decoder = json.JSONDecoder()

    try:
        obj, _end = decoder.raw_decode(cleaned)
        return obj
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    if start != -1:
        try:
            obj, _end = decoder.raw_decode(cleaned[start:])
            return obj
        except json.JSONDecodeError as exc:
            snippet = cleaned[:500]
            print(f"[gemini] JSON 파싱 실패. 원본 응답 일부:\n{snippet}")
            raise GeminiError(f"Gemini 응답을 JSON으로 해석하지 못했습니다: {exc}") from exc

    raise GeminiError("Gemini 응답에서 JSON 객체를 찾을 수 없습니다.")

def _wait_for_file_active(client: "genai.Client", file_obj, timeout_seconds: int = 120):
    start = time.time()
    current = file_obj
    while getattr(current.state, "name", current.state) == "PROCESSING":
        if time.time() - start > timeout_seconds:
            raise GeminiError("파일 처리 시간이 초과되었습니다. 다시 시도해주세요.")
        time.sleep(2)
        current = client.files.get(name=current.name)
    if getattr(current.state, "name", current.state) == "FAILED":
        raise GeminiError("Gemini가 업로드된 파일을 처리하지 못했습니다.")
    return current

def _call_gemini(
    system_instruction: str,
    prompt: str,
    model_name: Optional[str] = None,
    video_path: Optional[str] = None,
    image_paths: Optional[list[str]] = None,
) -> str:
    client = genai.Client(api_key=_get_api_key())
    contents = []

    # 멀티모달(영상 또는 이미지) 첨부 처리
    has_media = False
    if video_path and os.path.isfile(video_path):
        has_media = True
        uploaded = client.files.upload(file=video_path)
        uploaded = _wait_for_file_active(client, uploaded)
        contents.append(uploaded)
        
    if image_paths:
        for img_path in image_paths:
            if os.path.isfile(img_path):
                has_media = True
                uploaded = client.files.upload(file=img_path)
                uploaded = _wait_for_file_active(client, uploaded)
                contents.append(uploaded)

    target_model = _normalize_model(model_name, _DEFAULT_VIDEO_MODEL if has_media else _DEFAULT_MODEL)
    contents.append(prompt)

    try:
        response = client.models.generate_content(
            model=target_model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
            ),
        )
    except Exception as exc:
        raise GeminiError(f"Gemini API 호출 중 오류가 발생했습니다: {exc}") from exc

    if not response.candidates:
        raise GeminiError("Gemini가 응답을 반환하지 않았습니다.")

    text = getattr(response, "text", None)
    if not text:
        raise GeminiError("Gemini 응답에 텍스트 내용이 없습니다.")
    return text

def analyze_reference(
    ad_copy_text: str,
    video_path: Optional[str] = None,
    model_name: Optional[str] = None,
) -> tuple[dict[str, Any], str]:
    has_video = bool(video_path and os.path.isfile(video_path))
    if not ad_copy_text.strip() and not has_video:
        raise GeminiError("분석할 광고 카피 또는 영상 중 최소 하나는 필요합니다.")

    prompt = build_analysis_prompt(ad_copy_text=ad_copy_text, has_video=has_video)
    raw_text = _call_gemini(ANALYSIS_SYSTEM_INSTRUCTION, prompt, model_name=model_name, video_path=video_path)
    parsed = _extract_json(raw_text)
    return parsed, raw_text

def generate_plan(
    analysis_summary: str,
    product_name: str,
    product_usp_notes: str = "",
    landing_url: str = "",
    image_paths: Optional[list[str]] = None,
    model_name: Optional[str] = None,
) -> tuple[dict[str, Any], str]:
    if not analysis_summary.strip():
        raise GeminiError("레퍼런스 분석 결과가 없습니다. 먼저 레퍼런스 분석을 완료해주세요.")
    if not product_name.strip():
        raise GeminiError("제품명이 없습니다.")
        
    prompt = build_plan_prompt(
        analysis_summary=analysis_summary,
        product_name=product_name,
        product_usp_notes=product_usp_notes,
        landing_url=landing_url,
    )
    
    raw_text = _call_gemini(PLAN_SYSTEM_INSTRUCTION, prompt, model_name=model_name, image_paths=image_paths)
    parsed = _extract_json(raw_text)
    return parsed, raw_text