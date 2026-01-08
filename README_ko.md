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

> **당신의 프로젝트를 위한 완벽한 위키를 단 몇 분 만에 만들어보세요.**
> 
> **어떤 모델이든. 어떤 저장소든. 어떤 환경이든. 다 됩니다**

**Wiki As Readme**는 가장 유연한 AI 문서화 도구입니다. Ollama를 통한 로컬 Llama 3 모델 실행부터 Google Gemini Pro, OpenAI API 사용까지, 당신의 기술 스택에 완벽하게 적응합니다. GitHub, GitLab, Bitbucket과 같은 Git 플랫폼은 물론 로컬 폴더와도 원활하게 통합되어 최적의 문서화 솔루션을 제공합니다.

> [!NOTE]
> 몇몇 지원과 기능은 개발 중으로 **Wiki-As-Readme**는 PR을 환영합니다!

## ✨ 뛰어난 범용성 (Universal Compatibility)

이 프로젝트는 **플러그인 방식(Pluggable)** 으로 설계되었습니다. 실행 방식, 실행 위치, 그리고 기반이 되는 모델을 자유롭게 선택할 수 있습니다.

### 🧠 1. 모델 제약 없음 (Powered by LiteLLM)
*   **상용 API:** Google Vertex AI (Gemini), OpenAI (GPT-4), Anthropic (Claude), xAI (Grok).
*   **오픈 소스/로컬 모델:** **Ollama**, OpenRouter, HuggingFace.
*   **온프레미스:** 보안이 중요한 환경을 위해 자체 프라이빗 LLM 엔드포인트에 연결 가능합니다.

### 🚉 2. 플랫폼 제약 없음
*   **클라우드 저장소:** **GitHub**, **GitLab**, **Bitbucket**과 완벽하게 연동됩니다.
*   **로컬 개발:** 코드를 푸시하지 않고도 로컬 파일 시스템에서 직접 분석할 수 있습니다.
*   **프라이빗/엔터프라이즈:** 프라이빗 인스턴스 및 자체 호스팅 Git 서버를 완벽하게 지원합니다.

### 🛠️ 3. 배포 방식 제약 없음
*   **CI/CD:** GitHub Actions에 바로 적용할 수 있습니다.
*   **컨테이너:** Docker Compose를 통해 실행할 수 있습니다.
*   **서비스:** 웹훅(Webhooks)을 지원하는 상주형 API 서버로 배포할 수 있습니다.
*   **CLI:** 코딩 중에 로컬에서 즉시 실행 가능합니다.

## ⚡ 핵심 기능 (Core Features)
**🧠 심층 문맥 분석 (Deep Context Analysis):**\
문서를 작성하기 전에 파일 구조와 관계를 분석하여 프로젝트 아키텍처를 깊이 있게 이해합니다.

**📦 스마트한 구조 생성 (Smart Structure Generation):**\
문서화를 위한 논리적인 계층 구조(섹션 > 페이지)를 자동으로 결정합니다.

**🔍 포괄적인 콘텐츠 (Comprehensive Content):**\
아키텍처 개요, 설치 가이드, API 참조 등 상세한 페이지를 작성합니다.

**📊 자동 다이어그램 (Automatic Diagrams):**\
아키텍처 시각화를 위해 **Mermaid.js** 다이어그램(순서도, 시퀀스 등)을 자동 생성합니다.

**🚗 하이브리드 출력 (Hybrid Output):**\
개별 위키 마크다운 파일과 통합된 단일 `README.md`를 동시에 생성합니다.

**⚡ 비동기 및 확장성 (Async & Scalable):**\
**FastAPI**와 **AsyncIO**를 사용하여 대규모 문서화 작업도 효율적으로 처리합니다.

## 📖 예시 (Examples)

결과물이 궁금하신가요? **Wiki As Readme**가 생성한 예시들을 확인해보세요:

**[LangGraph 위키 예시 (영어)](examples/langgraph_readme_en.md)**
- 아키텍처 개요, 핵심 개념 및 Mermaid 다이어그램이 포함된 고품질 구조화 위키입니다.

**[LangGraph 위키 예시 (한국어)](examples/langgraph_readme_ko.md)**
- 동일한 내용을 한국어로 생성한 결과입니다.

**[Wiki As Readme 자체 위키](examples/wiki_as_README.md)**
- 이 프로젝트의 문서를 이 도구로 직접 생성한 결과입니다!

**[Notion 동기화 예시 (Live)](https://welcometogyuminworld.notion.site/Wiki-As-Readme-2e2b152141a48042837dcd05a9244b7a?source=copy_link)**
- 생성된 위키가 Notion 데이터베이스에 하위 페이지 및 구조화된 콘텐츠로 어떻게 자동 정리되는지 확인해보세요.

## 🚀 사용 모드 (Usage Modes)

이 프로젝트는 필요에 따라 다양한 방식으로 사용할 수 있습니다.

1.  **[GitHub Action (권장)](#1-github-action-권장)**
    - CI/CD 파이프라인에서 문서 업데이트를 자동화합니다.
2.  **[Docker Compose (로컬)](#2-docker-compose-로컬)**
    - Python 의존성 설치 없이 전체 UI/API를 로컬에서 실행합니다.
3.  **[로컬 Python 개발](#3-로컬-python-개발)**
    - 소스 코드를 수정하거나 직접 실행하려는 개발자를 위한 모드입니다.
4.  **[서버 및 웹훅](#4-서버-및-웹훅)**
    - 웹훅 지원과 함께 장기 실행 서비스로 배포합니다.

---

### 1. GitHub Action (권장)

저장소에 이 워크플로우를 추가하여 푸시가 발생할 때마다 `WIKI.md` 파일을 자동으로 업데이트하세요.

**🎮 수동 트리거 (Manual Trigger):**\
"Actions" 탭에서 워크플로우를 수동으로 실행하고 언어, 모델, 노션 동기화, 커밋 방식 등을 즉석에서 설정할 수 있습니다.

**📒 노션 동기화 (Notion Sync):**\
생성된 콘텐츠를 노션 데이터베이스와 선택적으로 동기화합니다.

**📤 Pull Requests:**\
브랜치에 직접 푸시하는 대신 검토를 위한 Pull Request를 생성할 수 있습니다.

1.  `.github/workflows/update-wiki.yml` 파일 생성:

    ```yaml
    name: Wiki-As-Readme As Action

    on:
      # 1. When pushing to main branch (runs automatically with defaults)
      push:
        branches:
          - main
        paths-ignore:
          - 'README.md'
          - 'WIKI.md'
          - '.github/workflows/update-wiki.yml'
      
      # 2. Manual trigger (allows custom input settings)
      # "Run workflow" menu in GitHub UI handles branch selection automatically.
      workflow_dispatch:
        inputs:
          language:
            description: 'Language code (e.g., ko, en, ja, etc.)'
            required: false
            default: 'en'
          llm_provider:
            description: 'LLM Provider (google, openai, anthropic, etc.)'
            required: false
            default: 'google'
          model_name:
            description: 'Model Name'
            required: false
            default: 'gemini-2.5-flash'
          sync_to_notion:
            description: 'Sync to Notion? (true/false)'
            type: boolean
            required: false
            default: false
          commit_method:
            description: 'How to apply changes'
            type: choice
            options:
              - push
              - pull-request
            default: 'push'

    jobs:
      wiki-time:
        runs-on: ubuntu-latest
        permissions:
          contents: write
          pull-requests: write

        env:
          WIKI_OUTPUT_PATH: "WIKI.md"

        steps:
          # 1. Checkout code
          # No 'ref' needed; it automatically checks out the branch selected in the "Run workflow" UI.
          - name: Checkout code
            uses: actions/checkout@v4

          # -----------------------------------------------------------------------
          # [OPTIONAL] GCP Credentials Setup
          # Create GCP key only if using Google Provider (defaults to 'google' if undefined)
          # -----------------------------------------------------------------------
          - name: Create GCP Credentials File
            if: ${{ (inputs.llm_provider == 'google') || (inputs.llm_provider == '') || (github.event_name == 'push') }}
            env:
              GCP_KEY: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS }}
            run: |
              if [ -n "$GCP_KEY" ]; then
                echo "$GCP_KEY" > ./gcp-key.json
              else
                echo "::warning::GOOGLE_APPLICATION_CREDENTIALS secret is missing, but provider is set to google."
              fi

          # 2. Generate Wiki Content & Sync
          - name: Generate Content (and Sync to Notion if enabled)
            uses: docker://ghcr.io/catuscio/wiki-as-readme-action:latest
            env:
              # --- Basic Settings ---
              # Use input if available, otherwise default to 'en' (e.g., for push events)
              LANGUAGE: ${{ inputs.language || 'en' }}
              WIKI_OUTPUT_PATH: ${{ env.WIKI_OUTPUT_PATH }}
              
              # --- LLM Provider and Model Settings ---
              LLM_PROVIDER: ${{ inputs.llm_provider || 'google' }}
              MODEL_NAME: ${{ inputs.model_name || 'gemini-2.5-flash' }}
              
              # --- API Key Settings ---
              
              # [GCP / Vertex AI]
              GCP_PROJECT_NAME: ${{ secrets.GCP_PROJECT_NAME }}
              GCP_MODEL_LOCATION: ${{ secrets.GCP_MODEL_LOCATION }}
              GOOGLE_APPLICATION_CREDENTIALS: /github/workspace/gcp-key.json
              
              # [Other Providers]
              OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
              ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
              
              # --- GitHub Token ---
              GIT_API_TOKEN: ${{ secrets.GITHUB_TOKEN }}

              # --- Notion Sync Settings ---
              # Pass "true" only if inputs.sync_to_notion is true; otherwise "false" (including push events)
              NOTION_SYNC_ENABLED: ${{ inputs.sync_to_notion || 'false' }}
              NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
              NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}

          # -----------------------------------------------------------------------
          # [OPTIONAL] GCP Credentials Cleanup
          # -----------------------------------------------------------------------
          - name: Remove GCP Credentials File
            if: always()
            run: rm -f ./gcp-key.json

          # 3. Commit and Push Changes (Update file in GitHub Repo)
          # Option A: Direct Push (default for push events or when 'push' is selected)
          - name: Commit and Push changes
            if: ${{ inputs.commit_method == 'push' || github.event_name == 'push' }}
            uses: stefanzweifel/git-auto-commit-action@v5
            with:
              commit_message: "✨📚 Update ${{ env.WIKI_OUTPUT_PATH }} via Wiki-As-Readme Action (${{ inputs.language || 'en' }})"
              file_pattern: ${{ env.WIKI_OUTPUT_PATH }}

          # Option B: Create Pull Request (when 'pull-request' is selected)
          - name: Create Pull Request
            if: ${{ inputs.commit_method == 'pull-request' }}
            uses: peter-evans/create-pull-request@v7
            with:
              title: "✨📚 Update ${{ env.WIKI_OUTPUT_PATH }} via Wiki-As-Readme Action"
              body: |
                This PR was automatically generated by [Wiki-As-Readme](https://github.com/catuscio/wiki-as-readme) Action.
                
                It includes the following changes:
                - Updated wiki content in **${{ env.WIKI_OUTPUT_PATH }}** based on the current state of the repository.
                - (If enabled) Synchronized changes to the linked Notion database.            

                ---

                > 📖 Powered by [Wiki-As-Readme](https://github.com/catuscio/wiki-as-readme)
                > Turn your codebase into a comprehensive Wiki in minutes, delivered in a single Readme.
                > Works with Any Model. Any Repo. Any Environment.
              branch: wiki-update-${{ github.run_id }}
              commit-message: "✨📚 Update ${{ env.WIKI_OUTPUT_PATH }} via Wiki-As-Readme Action (${{ inputs.language || 'en' }})"
              add-paths: ${{ env.WIKI_OUTPUT_PATH }}
    ```

### 2. Docker Compose (로컬)

명령어 한 줄로 로컬에서 애플리케이션을 실행하세요. UI를 체험해보기 가장 쉬운 방법입니다.

1.  **`.env` 설정**:
    `.env example`을 `.env`로 복사하세요.
    -   API 키를 설정하세요 (예: `LLM_PROVIDER`, `OPENAI_API_KEY`, 또는 `GCP_...`).
    -   (선택 사항) 노션 동기화 설정(`NOTION_SYNC_ENABLED` 등)을 구성하거나 대상 코드를 가리키도록 `LOCAL_REPO_PATH`를 변경하세요.

2.  **실행**:
    ```bash
    docker-compose up --build
    ```
3.  **접속**:
    -   **웹 UI**: `http://localhost:8501`
        -   _팁: 사이드바의 **History** 탭을 사용하여 이전에 생성된 위키를 확인하고 다운로드할 수 있습니다._
    -   **API 문서**: `http://localhost:8000/docs`

### 3. 로컬 Python 개발

소스 코드를 수정하거나 도커 없이 실행하려는 경우입니다.

**필수 조건:** Python 3.12+, [uv](https://github.com/astral-sh/uv).

1.  **복제 및 설치**:
    ```bash
    git clone https://github.com/catuscio/wiki-as-readme.git
    cd wiki-as-readme
    uv sync
    source .venv/bin/activate
    ```

2.  **`.env` 설정**:
    `.env example`을 `.env`로 복사하고 변수를 설정하세요.

3.  **백엔드 실행**:
    ```bash
    uv run uvicorn src.server:app --reload --port 8000
    ```

4.  **프론트엔드 실행**:
    ```bash
    uv run streamlit run src/app.py
    ```

### 4. 서버 및 웹훅

GitHub 등의 웹훅 요청을 처리할 수 있는 API 서버로 배포할 수 있습니다.

*   **엔드포인트**: `POST /api/v1/webhook/github`
*   **페이로드**: 표준 GitHub push 이벤트 페이로드.
*   **동작**: 저장소에 대한 위키 생성 백그라운드 작업을 트리거하고 결과를 다시 커밋합니다 (`GIT_API_TOKEN` 필요).

### 설정 참조 (`.env`)

로컬이나 도커 환경 모두 환경 변수를 통해 설정합니다:

| 카테고리 | 변수명 | 설명 | 예시 |
| :--- | :--- | :--- | :--- |
| **LLM Provider** | `LLM_PROVIDER` | `google`, `openai`, `anthropic`, `xai`, `openrouter`, `ollama` | `google` |
| | `MODEL_NAME` | 사용할 모델 식별자 | `gemini-2.5-flash` |
| | `LLM_BASE_URL` | 커스텀 기본 URL (예: Ollama/프록시) | `http://localhost:11434/v1` |
| **인증** | `OPENAI_API_KEY` | OpenAI API 키 | `sk-...` |
| | `ANTHROPIC_API_KEY` | Anthropic API 키 | `sk-ant...` |
| | `GCP_PROJECT_NAME` | Vertex AI 프로젝트 ID | `my-genai-project` |
| **노션 동기화** | `NOTION_SYNC_ENABLED` | 생성 후 노션 동기화 여부 | `true` |
| | `NOTION_API_KEY` | 노션 통합 토큰 | `secret_...` |
| | `NOTION_DATABASE_ID` | 대상 노션 데이터베이스 ID | `abc123...` |
| **경로** | `WIKI_OUTPUT_PATH` | 생성된 위키 저장 경로 (기본값: `WIKI.md` 또는 `./output`) | `./output/WIKI.md` |
| | `LOCAL_REPO_PATH` | 도커 마운트용 로컬 저장소 경로 | `/Users/me/project` |
| **고급 설정** | `USE_STRUCTURED_OUTPUT`| 네이티브 JSON 모드 사용 여부 | `true` |
| | `IGNORED_PATTERNS` | 제외할 파일 패턴 (**JSON 배열**) | `'["*.log", "node_modules/*"]'` |


## 🔌 API 명세

백엔드 API는 FastAPI로 구축되었습니다. 서버 실행 시 `http://localhost:8000/docs`에서 대화형 Swagger 문서를 확인할 수 있습니다.

### 위키 생성

#### `POST /api/v1/wiki/generate/file`
백그라운드에서 위키 생성을 시작하고 결과를 서버에 마크다운 파일로 저장합니다.

**요청 본문:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "repo_type": "github",
  "language": "en",
  "is_comprehensive_view": true
}
```

#### `POST /api/v1/wiki/generate/text`
백그라운드에서 위키 생성을 시작합니다. 결과 텍스트는 작업 상태에 저장됩니다.

#### `GET /api/v1/wiki/status/{task_id}`
생성 작업의 상태와 결과를 조회합니다.

### 웹훅

#### `POST /api/v1/webhook/github`
GitHub 웹훅(Push 이벤트) 엔드포인트입니다. `main` 브랜치 푸시 시 자동으로 위키 생성을 트리거합니다.

## 🛠️ 아키텍처

*   **Frontend:** [Streamlit](https://streamlit.io/) (사용자 인터페이스)
*   **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (REST API, 백그라운드 작업)
*   **LLM Integration:** [LiteLLM](https://docs.litellm.ai/) (100개 이상의 LLM 통합 인터페이스)
*   **Data Models:** [Pydantic](https://docs.pydantic.dev/) (타입 안전성 및 검증)
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

*   이 프로젝트는 AsyncFuncAI의 [deepwiki-open](https://github.com/AsyncFuncAI/deepwiki-open) 프로젝트의 핵심 로직을 활용하고 많은 영향을 받았습니다.
*   오픈 소스 라이브러리의 힘으로 만들어졌습니다.
*   더 나은 자동화된 문서화에 대한 필요성에서 영감을 받았습니다.