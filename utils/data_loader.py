from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_DATA: Dict[str, Any] = {
    "metadata": {
        "title": "기본 입시 가이드(폴백)",
        "version": "fallback",
        "last_updated": "N/A",
        "notice": "데이터 파일을 읽지 못해 기본 샘플을 사용 중입니다. 공식 공지를 반드시 확인하세요.",
    },
    "categories": [
        {
            "id": "fallback",
            "name": "기본 안내",
            "description": "데이터 파일 문제 시 제공되는 기본 항목",
            "items": [
                {
                    "title": "데이터 파일 점검 필요",
                    "summary": "data/admissions_guide.json 파일 존재 여부와 JSON 형식을 확인하세요.",
                    "details": [
                        "파일 경로가 정확한지 확인",
                        "JSON 문법 오류(쉼표/따옴표)를 점검",
                        "복구 후 앱을 다시 실행",
                    ],
                    "keywords": ["fallback", "json", "오류"],
                }
            ],
        }
    ],
}


def load_admissions_data(path: str = "data/admissions_guide.json") -> Dict[str, Any]:
    """입시 JSON을 읽고 실패 시 안전한 폴백 데이터를 반환한다."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
        parsed = json.loads(raw)
        if not isinstance(parsed, dict) or "categories" not in parsed:
            return DEFAULT_DATA
        return parsed
    except Exception:
        return DEFAULT_DATA


def flatten_items(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """검색과 컨텍스트 생성을 위해 category/item 구조를 평탄화한다."""
    flattened: List[Dict[str, Any]] = []
    for category in data.get("categories", []):
        category_name = category.get("name", "미분류")
        for item in category.get("items", []):
            flattened.append(
                {
                    "category_id": category.get("id", "unknown"),
                    "category_name": category_name,
                    "title": item.get("title", "제목 없음"),
                    "summary": item.get("summary", ""),
                    "details": item.get("details", []),
                    "keywords": item.get("keywords", []),
                }
            )
    return flattened


def search_items(data: Dict[str, Any], keyword: str, top_n: int = 5) -> List[Dict[str, Any]]:
    """제목/요약/키워드에서 단순 포함 검색 후 상위 N개를 반환한다."""
    query = keyword.strip().lower()
    if not query:
        return []

    results: List[Dict[str, Any]] = []
    for item in flatten_items(data):
        haystack = " ".join(
            [
                str(item.get("title", "")),
                str(item.get("summary", "")),
                " ".join(item.get("keywords", [])),
                " ".join(item.get("details", [])),
                item.get("category_name", ""),
            ]
        ).lower()
        if query in haystack:
            results.append(item)

    return results[:top_n]


def build_context_from_items(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "앱 내 참고자료 검색 결과가 없습니다."

    lines = ["[앱 내 참고자료]"]
    for index, item in enumerate(items, start=1):
        details = "; ".join(item.get("details", [])[:3])
        lines.append(
            f"{index}. [{item.get('category_name')}] {item.get('title')} - {item.get('summary')} | 핵심: {details}"
        )
    return "\n".join(lines)
