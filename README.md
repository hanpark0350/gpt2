# 대입 정보 허브 + Gemini Q&A (Streamlit)

한국 고등학생의 대입 준비를 돕기 위한 **입시 정보 모음 + AI 질의응답** 웹앱입니다.

- 입시 정보는 로컬 JSON(`data/admissions_guide.json`)에서 로드
- 검색 결과를 Gemini 컨텍스트로 주입해 답변 보강
- API Key는 사용자 세션 메모리에만 저장(파일 저장 없음)
- 고정 모델: `gemini-3-flash-preview`

## 1) 설치

```bash
pip install -r requirements.txt
```

## 2) 실행

```bash
streamlit run app.py
```

## 3) 사용 방법

1. 좌측 사이드바에서 `Gemini API Key` 입력
2. `입시 정보` 탭에서 키워드 검색 및 카테고리 탐색
3. `AI 질문하기` 탭에서 질문 입력 후 답변 생성
4. `히스토리` 탭에서 질문/답변 내역 확인 및 초기화

## 4) API Key 입력 위치

- 앱 실행 후 좌측 사이드바의 `Gemini API Key` 입력란
- `type="password"`로 마스킹 처리
- 세션 메모리에만 저장되고 서버 재시작 시 초기화

## 5) 데이터(JSON) 수정 방법

`data/admissions_guide.json`의 카테고리/아이템/키워드를 수정하면 앱 콘텐츠가 즉시 변경됩니다.

예시 구조:

```json
{
  "metadata": {"title": "...", "notice": "..."},
  "categories": [
    {
      "id": "tracks",
      "name": "전형 이해",
      "description": "...",
      "items": [
        {
          "title": "학생부교과전형 핵심",
          "summary": "...",
          "details": ["..."],
          "keywords": ["내신", "수능최저"]
        }
      ]
    }
  ]
}
```

## 6) 주의사항

- 본 앱의 AI 답변은 일반 가이드이며, 최신 모집요강/공식 발표를 대체하지 않습니다.
- 전형 요소(수능최저, 반영비율, 면접방식 등)는 해마다 변경될 수 있으므로 대학 입학처 공지를 반드시 확인하세요.
- 네트워크/쿼터/API 키 오류 시 사용자 친화 메시지를 표시합니다.
