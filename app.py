from __future__ import annotations

import streamlit as st

from services.gemini_client import generate_answer, validate_api_key_format
from ui.components import render_disclaimer, render_search_results, render_template_buttons
from utils.data_loader import build_context_from_items, flatten_items, load_admissions_data, search_items

MODEL_NAME = "gemini-3-flash-preview"


def init_state() -> None:
    st.session_state.setdefault("api_key", "")
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("last_results", [])
    st.session_state.setdefault("last_context", "앱 내 참고자료 검색 결과가 없습니다.")
    st.session_state.setdefault("last_called_at", None)
    st.session_state.setdefault("pending_question", "")


def sidebar_settings() -> None:
    with st.sidebar:
        st.header("설정")
        api_key_input = st.text_input("Gemini API Key", type="password", value=st.session_state["api_key"])
        st.session_state["api_key"] = api_key_input.strip()

        is_valid, message = validate_api_key_format(st.session_state["api_key"])
        if st.session_state["api_key"]:
            (st.success if is_valid else st.warning)(message)
        else:
            st.info("API Key를 입력하면 AI 질문 기능이 활성화됩니다.")

        st.text_input("사용 모델", value=MODEL_NAME, disabled=True)

        if st.button("세션 초기화"):
            st.session_state["api_key"] = ""
            st.session_state["chat_history"] = []
            st.session_state["last_results"] = []
            st.session_state["last_context"] = "앱 내 참고자료 검색 결과가 없습니다."
            st.session_state["last_called_at"] = None
            st.session_state["pending_question"] = ""
            st.rerun()


def render_home_tab(data: dict) -> None:
    st.subheader("한국 고등학생을 위한 대입 정보 허브 + AI 도우미")
    st.write(data.get("metadata", {}).get("notice", ""))
    render_disclaimer()
    st.markdown(
        """
        ### 사용 방법
        1. 좌측 사이드바에서 API Key를 입력하세요.
        2. **입시 정보** 탭에서 키워드 검색 및 카테고리 탐색을 먼저 진행하세요.
        3. **AI 질문하기** 탭에서 질문하면 검색 결과를 참고해 답변합니다.
        4. **히스토리** 탭에서 이전 질문/답변을 확인하거나 초기화할 수 있습니다.
        """
    )


def render_info_tab(data: dict) -> None:
    st.subheader("입시 정보 보기")
    query = st.text_input("키워드 검색", placeholder="예: 학생부종합, 수능최저, 면접")
    if query:
        results = search_items(data, query, top_n=6)
        st.session_state["last_results"] = results
        st.session_state["last_context"] = build_context_from_items(results)
        st.markdown("#### 검색 결과")
        render_search_results(results)

        if results and st.button("이 자료를 바탕으로 AI에게 질문하기"):
            st.session_state["pending_question"] = f"'{query}' 관련해서 내 상황에 맞는 준비 전략을 제안해줘."
            st.success("AI 질문하기 탭으로 이동해 질문을 확인하세요.")
    else:
        st.caption("카테고리별로 자료를 먼저 둘러보세요.")

    st.markdown("---")
    st.markdown("#### 카테고리별 탐색")
    for category in data.get("categories", []):
        with st.expander(f"{category.get('name', '미분류')} | {category.get('description', '')}"):
            for item in category.get("items", []):
                st.markdown(f"**{item.get('title', '제목 없음')}**")
                st.write(item.get("summary", ""))
                for detail in item.get("details", []):
                    st.markdown(f"- {detail}")
                st.caption(f"키워드: {', '.join(item.get('keywords', []))}")


def render_ai_tab() -> None:
    st.subheader("AI 질문하기")
    render_disclaimer()

    if not st.session_state["api_key"]:
        st.warning("AI 기능을 사용하려면 좌측 사이드바에서 Gemini API Key를 입력해주세요.")
        st.stop()

    template = render_template_buttons()
    default_question = template or st.session_state.get("pending_question", "")

    question = st.text_area("질문 입력", value=default_question, placeholder="학년/목표 대학군/관심 전형을 함께 적어보세요.")

    col1, col2 = st.columns([1, 1])
    ask = col1.button("AI 답변 받기", type="primary")
    retry = col2.button("마지막 질문 재시도")

    target_question = question.strip()
    if retry and st.session_state["chat_history"]:
        target_question = st.session_state["chat_history"][-1]["question"]

    if ask or retry:
        if not target_question:
            st.warning("질문을 입력해주세요.")
            return

        context = st.session_state.get("last_context", "앱 내 참고자료 검색 결과가 없습니다.")
        with st.spinner("Gemini가 답변을 생성 중입니다..."):
            answer, called_at = generate_answer(
                api_key=st.session_state["api_key"],
                user_query=target_question,
                context=context,
                model=MODEL_NAME,
                last_called_at=st.session_state.get("last_called_at"),
            )

        st.session_state["last_called_at"] = called_at
        st.session_state["chat_history"].append(
            {"question": target_question, "answer": answer, "context": context}
        )
        st.session_state["pending_question"] = ""

        st.markdown("### 답변")
        st.write(answer)


def render_history_tab() -> None:
    st.subheader("내 질문 히스토리")
    history = st.session_state.get("chat_history", [])
    if not history:
        st.info("아직 질문 내역이 없습니다.")
        return

    for idx, entry in enumerate(reversed(history), start=1):
        with st.expander(f"{idx}. {entry['question'][:60]}"):
            st.markdown("**질문**")
            st.write(entry["question"])
            st.markdown("**답변**")
            st.write(entry["answer"])
            st.markdown("**참고 컨텍스트**")
            st.code(entry["context"])

    if st.button("대화 초기화"):
        st.session_state["chat_history"] = []
        st.success("히스토리를 초기화했습니다.")


def render_help_tab(data: dict) -> None:
    st.subheader("도움말 / 주의사항")
    st.markdown(
        """
        - 본 앱은 **일반적인 입시 준비 가이드**를 제공합니다.
        - 대학별 세부 전형(반영비율/최저/면접 방식)은 매년 달라질 수 있습니다.
        - 반드시 대학 입학처 공지, 교육청 자료, 학교 진학지도를 함께 확인하세요.
        - API Key는 세션 메모리에만 저장되며 파일로 저장하지 않습니다.
        """
    )
    st.json(data.get("metadata", {}))


def main() -> None:
    st.set_page_config(page_title="대입 정보 허브 + AI", page_icon="🎓", layout="wide")
    init_state()

    data = load_admissions_data()
    sidebar_settings()

    tabs = st.tabs(["Home", "입시 정보", "AI 질문하기", "히스토리", "도움말"])

    with tabs[0]:
        render_home_tab(data)
    with tabs[1]:
        render_info_tab(data)
    with tabs[2]:
        render_ai_tab()
    with tabs[3]:
        render_history_tab()
    with tabs[4]:
        render_help_tab(data)


if __name__ == "__main__":
    main()
