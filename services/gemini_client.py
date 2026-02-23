from __future__ import annotations

import time
from typing import Tuple

from google import genai

from utils.prompt_builder import build_system_instruction, build_user_prompt


MIN_INTERVAL_SECONDS = 1.5


def validate_api_key_format(api_key: str) -> Tuple[bool, str]:
    key = api_key.strip()
    if not key:
        return False, "API Key를 입력해주세요."
    if len(key) < 20:
        return False, "API Key 형식이 올바르지 않은 것 같습니다. 키를 다시 확인해주세요."
    return True, "사용 가능한 형식입니다."


def generate_answer(
    api_key: str,
    user_query: str,
    context: str,
    model: str = "gemini-3-flash-preview",
    last_called_at: float | None = None,
) -> Tuple[str, float]:
    """Gemini 호출 래퍼: 예외를 사용자 친화 메시지로 변환한다."""
    now = time.time()
    if last_called_at and now - last_called_at < MIN_INTERVAL_SECONDS:
        return (
            "요청이 너무 빠릅니다. 잠시 후 다시 질문해주세요 (약 1~2초 간격 권장).",
            last_called_at,
        )

    try:
        client = genai.Client(api_key=api_key.strip())
        response = client.models.generate_content(
            model=model,
            contents=build_user_prompt(user_query=user_query, context=context),
            config={"system_instruction": build_system_instruction()},
        )

        text = (response.text or "").strip()
        if not text:
            return (
                "응답이 비어 있습니다. 질문을 조금 더 구체적으로 작성해 다시 시도해주세요.",
                now,
            )
        return text, now

    except Exception as exc:  # broad 예외를 사용자 메시지로 표준화
        error_message = str(exc).lower()
        if "api key" in error_message or "authentication" in error_message or "permission" in error_message:
            return "API Key가 유효하지 않거나 권한이 없습니다. 키를 다시 확인해주세요.", now
        if "quota" in error_message or "rate" in error_message:
            return "요청 한도에 도달했습니다. 잠시 후 다시 시도해주세요.", now
        if "timeout" in error_message or "network" in error_message:
            return "네트워크 또는 시간 초과 오류가 발생했습니다. 잠시 후 다시 시도해주세요.", now
        return "요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.", now
