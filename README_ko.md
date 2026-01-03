# 📚 Wiki As Readme

<p align="center">
  <img src="public/wiki-as-readme-banner.png" alt="Wiki as Readme Banner">
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/Language-English-green.svg" alt="English"></a>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-orange?style=flat)](https://docs.litellm.ai/)

> **코드 몇 줄만으로 당신의 프로젝트를 위한 완벽한 위키를 만들어보세요.**

**Wiki As Readme**는 Git 리포지토리(GitHub, GitLab, Bitbucket 또는 로컬)를 분석하여 구조화되고 상세한 위키를 자동으로 생성해주는 AI 기반 도구입니다. 최신 LLM(via **LiteLLM**)을 활용하여 코드 구조를 파악하고, 소스 코드를 읽어 전문가 수준의 문서를 작성하며, Mermaid 다이어그램까지 자동으로 생성합니다.

## ✨ 주요 기능

*   **🤖 멀티 LLM 지원:**
    *   **LiteLLM**을 기반으로 **Google Vertex AI (Gemini)**, **OpenAI (GPT-4)**, **Anthropic (Claude)**, **xAI (Grok)**, **Ollama**, **OpenRouter** 등 다양한 모델을 지원합니다.
*   **🧠 심층 문맥 분석:**
    *   문서를 작성하기 전에 파일 구조와 모듈 간의 관계를 분석하여 프로젝트의 아키텍처를 깊이 있게 이해합니다.
*   **📦 스마트한 구조 생성:**
    *   문서화를 위한 논리적인 계층 구조(섹션 > 페이지)를 자동으로 결정합니다.
*   **🔍 포괄적인 콘텐츠:**
    *   아키텍처 개요, 설치 가이드, API 참조 등 상세한 페이지를 작성합니다.
*   **📊 자동 다이어그램 생성:**
    *   아키텍처를 시각화하기 위해 **Mermaid.js** 다이어그램(순서도, 시퀀스 다이어그램, 클래스 다이어그램)을 자동으로 생성합니다.
*   **🚉 다양한 저장소 지원:**
    *   **GitHub**, **GitLab**, **Bitbucket** 및 **로컬 파일 시스템**과 원활하게 작동합니다.
*   **🚗 하이브리드 출력:**
    *   위키를 위한 개별 마크다운 파일과 모든 내용을 통합한 단일 `README.md` 파일을 동시에 생성합니다.
*   **⚡ 비동기 및 확장성:**
    *   **FastAPI**와 **AsyncIO**로 구축되어 대규모 문서화 작업도 효율적으로 처리합니다.

## 🚀 시작하기

### 필수 조건

*   **Python 3.12** 이상
*   **[uv](https://github.com/astral-sh/uv)** (의존성 관리 도구로 권장)
*   선택한 LLM 제공업체의 **API 키** (예: Google Cloud Project, OpenAI API Key)

### 설치

1.  **리포지토리 복제**

    ```bash
    git clone https://github.com/catuscio/wiki-as-readme.git
    cd wiki-as-readme
    ```

2.  **`uv`를 사용하여 의존성 설치**

    ```bash
    # uv가 설치되어 있지 않다면 설치
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # 의존성 동기화
    uv sync
    ```

3.  **가상 환경 활성화**

    ```bash
    source .venv/bin/activate
    ```

### 설정 (`.env`)

이 프로젝트는 LLM 설정과 API 키를 포함한 구성을 위해 `.env` 파일을 사용합니다.

1.  **예제 파일 복사:**

    ```bash
    cp ".env example" .env
    ```

2.  **`.env` 파일 수정 및 필수 변수 설정:**

    | 카테고리 | 변수명 | 설명 | 예시 |
    | :--- | :--- | :--- | :--- |
    | **LLM 제공업체** | `LLM_PROVIDER` | 제공업체 선택: `google`, `openai`, `anthropic`, `xai`, `openrouter`, `ollama` | `google` |
    | | `MODEL_NAME` | 사용할 모델 식별자 | `gemini-2.0-flash-exp` 또는 `gpt-4o` |
    | **인증 (택 1)** | `OPENAI_API_KEY` | OpenAI 사용 시 | `sk-...` |
    | | `ANTHROPIC_API_KEY`| Anthropic 사용 시 | `sk-ant-...` |
    | | `GCP_PROJECT_NAME` | **(Google 전용)** Vertex AI 프로젝트 ID | `my-genai-project` |
    | | `GCP_MODEL_LOCATION`| **(Google 전용)** 리전 | `us-central1` |
    | **고급 LLM 설정** | `USE_STRUCTURED_OUTPUT`| 네이티브 JSON 모드 사용 (모델 지원 필요) | `true` |
    | **필터링** | `IGNORED_PATTERNS` | 분석에서 제외할 파일 패턴 (**JSON 배열**) | `'["*.log", "node_modules/*"]'` |
    | **Git 접근** | `GIT_API_TOKEN` | **비공개 리포지토리** 접근 및 속도 제한 방지를 위해 중요 | `ghp_...` |
    | **앱 설정** | `API_BASE_URL` | 백엔드 API 주소 | `http://localhost:8000/api/v1` |
    | | `language` | 위키 생성 언어 | `en`, `ko`, `ja` |

#### 상세 설정

*   **`USE_STRUCTURED_OUTPUT`**:
    *   `true`로 설정 시, LLM의 네이티브 구조화된 출력 기능(예: Gemini의 JSON 모드, OpenAI의 Structured Outputs)을 사용합니다.
    *   생성된 위키 구조의 신뢰성을 크게 높이고 메타데이터의 일관성을 보장합니다.
    *   **권장 사항:** Gemini 1.5 Pro/Flash, GPT-4o, Claude 3.5 Sonnet과 같은 최신 모델에서는 `true`로 유지하세요.
*   **`IGNORED_PATTERNS`**:
    *   AI 분석에서 특정 파일이나 디렉토리를 제외할 수 있습니다.
    *   **토큰 최적화에 필수적입니다**: 거대한 의존성 폴더(`node_modules`), 빌드 결과물(`dist`, `build`), 락 파일(`uv.lock`, `package-lock.json`) 등을 제외하여 비용을 절약하고 LLM이 중요한 내용에 집중하게 합니다.
    *   **형식**: 반드시 한 줄로 된 JSON 배열 문자열이어야 합니다 (예: `'["*.png", "docs/*"]'`).

    > **Google Vertex AI 사용자 참고:**
    > 로컬 환경에서 gcloud를 사용하여 인증해야 합니다:
    > ```bash
    > gcloud auth application-default login
    > ```

## 💻 사용 방법

애플리케이션은 **FastAPI 백엔드**와 **Streamlit 프론트엔드** 두 부분으로 구성되어 있습니다. 두 가지를 모두 실행해야 합니다.

### 1. 백엔드 API 시작

터미널을 열고 다음을 실행하세요:

```bash
uv run uvicorn src.server:app --reload --port 8000
```

### 2. Streamlit UI 시작

**새로운** 터미널 창을 열고 다음을 실행하세요:

```bash
uv run streamlit run src/app.py
```

### 3. 위키 생성

1.  브라우저에서 Streamlit 주소(보통 `http://localhost:8501`)로 접속합니다.
2.  **리포지토리 정보:** 리포지토리 URL(예: `https://github.com/owner/repo`) 또는 로컬 경로를 입력합니다.
3.  **설정:** "Comprehensive View"(포괄적 보기)를 켜거나 언어를 변경합니다.
4.  **✨ Generate Wiki** 버튼을 클릭합니다.
5.  작업이 완료될 때까지 기다립니다 (백그라운드에서 실행됨).
6.  **다운로드:** 완료되면 내용을 미리보고 통합된 `README.md` 파일을 다운로드할 수 있습니다.

## 🔌 API 명세

백엔드 API는 FastAPI로 구축되었습니다. 서버 실행 시 `http://localhost:8000/docs`에서 대화형 Swagger 문서를 확인할 수 있습니다.

### 위키 생성

#### `POST /api/v1/wiki/generate/file`
백그라운드에서 위키 생성을 시작하고 결과를 서버에 마크다운 파일로 저장합니다.

**요청 본문(Request Body):**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "repo_type": "github",
  "language": "ko",
  "is_comprehensive_view": true
}
```

#### `POST /api/v1/wiki/generate/text`
백그라운드에서 위키 생성을 시작합니다. 생성된 텍스트는 작업 상태 조회 시 확인할 수 있습니다.

#### `GET /api/v1/wiki/status/{task_id}`
생성 작업의 상태와 결과물을 조회합니다.

### 웹훅 (Webhooks)

#### `POST /api/v1/webhook/github`
GitHub 웹훅(Push 이벤트) 수신 엔드포인트입니다. `main` 브랜치에 푸시가 발생하면 자동으로 위키 생성을 트리거합니다.

## 📖 예시

결과물이 궁금하신가요? **Wiki As Readme**가 생성한 고품질 문서를 확인해보세요:

*   **[LangGraph 위키 예시 (영어)](examples/langgraph_readme_en.md)**: [LangGraph](https://github.com/langchain-ai/langchain-ai/langgraph) 리포지토리를 기반으로 생성된 고품질 구조화 위키입니다. 아키텍처 개요, 핵심 개념 및 Mermaid 다이어그램을 포함하고 있습니다.
*   **[LangGraph 위키 예시 (한국어)](examples/langgraph_readme_ko.md)**: 동일한 LangGraph 위키를 한국어로 생성한 결과물입니다.
*   **[Wiki As Readme 프로젝트 자체 위키](examples/wiki_as_README.md)**: 바로 이 프로젝트의 문서를 이 도구로 직접 생성한 예시입니다!

## 🐳 Docker 지원

Docker Compose를 사용하여 API 서버를 실행할 수도 있습니다.

```bash
docker-compose up --build
```
*참고: 현재는 API 서버(8000번 포트)만 시작합니다. Streamlit 앱은 로컬에서 실행하거나 컴포즈 파일을 수정해야 합니다.*

## 🛠️ 아키텍처

*   **Frontend:** [Streamlit](https://streamlit.io/) (사용자 인터페이스)
*   **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (REST API, 백그라운드 작업)
*   **LLM Integration:** [LiteLLM](https://docs.litellm.ai/) (100개 이상의 LLM을 위한 통합 인터페이스)
*   **Data Models:** [Pydantic](https://docs.pydantic.dev/) (타입 안전성 & 구조화된 출력 검증)
*   **Diagrams:** Mermaid.js

## 🤝 기여하기

기여는 언제나 환영합니다! Pull Request를 보내주세요.

1.  프로젝트를 Fork 합니다.
2.  새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/AmazingFeature`).
3.  변경 사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`).
4.  브랜치에 푸시합니다 (`git push origin feature/AmazingFeature`).
5.  Pull Request를 생성합니다.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

-----

### 감사의 말

*   이 프로젝트는 [deepwiki-open](https://github.com/AsyncFuncAI/deepwiki-open) 프로젝트의 핵심 로직을 활용하고 많은 영향을 받았습니다.
*   오픈 소스 라이브러리의 힘으로 만들어졌습니다.
*   더 나은 자동화된 문서화에 대한 필요성에서 영감을 받았습니다.
