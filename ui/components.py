from __future__ import annotations

import streamlit as st


DISCLAIMER = (
    "⚠️ 본 앱의 답변은 일반적인 참고용 가이드입니다. "
    "전형 방법, 일정, 반영 비율은 매년/대학별로 달라질 수 있으므로 "
    "반드시 대학 입학처·교육청·학교의 최신 공식 공지를 확인하세요."
)


def render_disclaimer() -> None:
    st.info(DISCLAIMER)


def render_template_buttons() -> str | None:
    st.caption("빠르게 시작하는 템플릿 질문")
    col1, col2, col3 = st.columns(3)
    selected = None

    if col1.button("학생부종합 준비 체크리스트"):
        selected = "고2 학생 기준으로 학생부종합전형 준비 체크리스트를 알려줘."
    if col2.button("OO대 전형 비교"):
        selected = "목표 대학군 3곳의 전형 요소를 비교할 때 무엇을 우선 봐야 해?"
    if col3.button("내신/수능 병행 전략"):
        selected = "내신과 수능을 병행할 때 주간 학습 루틴 예시를 제안해줘."

    return selected


def render_search_results(results: list[dict]) -> None:
    if not results:
        st.write("검색 결과가 없습니다.")
        return

    for item in results:
        with st.expander(f"[{item['category_name']}] {item['title']}"):
            st.write(item["summary"])
            for detail in item.get("details", []):
                st.markdown(f"- {detail}")
            st.caption(f"키워드: {', '.join(item.get('keywords', []))}")
