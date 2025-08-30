# 🚀 MCP 서버 실습 종합 가이드

## 📋 프로젝트 개요

이 프로젝트는 **MCP(Model Context Protocol) 서버**를 구축하고 다양한 AI 도구들을 연동하는 실습 프로젝트입니다. 수학 연산, 파일 검색, PDF 기반 RAG 시스템, Office 문서 처리 등 다양한 기능을 MCP 프로토콜을 통해 제공합니다.

### 🎯 실습 목표

- MCP 서버의 개념과 구조 이해
- 다양한 도구들의 MCP 서버 구현
- LangChain을 활용한 RAG 시스템 구축
- AI 모델과 외부 도구의 연동 방법 학습
- 보안을 고려한 API 키 관리 방법 습득

---

## 🏗️ 프로젝트 구조

```
test-server/
├── 📁 explorer-server/          # 파일 검색 MCP 서버
│   └── main.py                  # D 드라이브 파일 검색 도구
├── 📁 math-server/              # 수학 연산 MCP 서버
│   └── math_server.py           # 덧셈, 뺄셈 도구
├── 📁 rag-server/               # RAG 시스템 MCP 서버
│   ├── main.py                  # PDF 기반 질문응답
│   ├── office.py                # Office 문서 기반 질문응답
│   ├── office/                  # 테스트용 Office 문서들
│   │   ├── 미세먼지가 치매에 미치는 영향.docx
│   │   ├── 자동차_리뷰.xlsx
│   │   ├── 책_리뷰.xlsx
│   │   └── 한옥의 장점과 단점.docx
│   ├── mcp_rag_practice_summary.pdf
│   ├── 실습_가이드.html
│   └── 실습_정리.md
└── 📁 test-server/              # 기존 테스트 코드들
    ├── mcp_client.py
    ├── mcp_server.py
    ├── sse_client.py
    ├── sse_server.py
    └── function_calling.py
```

---

## 🔧 MCP 서버란?

**MCP(Model Context Protocol)**는 AI 모델과 다양한 도구, 데이터 소스를 연결하는 표준 프로토콜입니다.

### 주요 특징

- **도구 등록**: 다양한 기능을 도구로 등록하여 AI가 활용할 수 있게 함
- **프로토콜 표준화**: AI 모델과 도구 간의 통신을 표준화
- **확장성**: 새로운 도구를 쉽게 추가할 수 있음
- **크로스 플랫폼**: 다양한 환경에서 동작

### MCP 서버 기본 구조

```python
from mcp.server.fastmcp import FastMCP

# MCP 서버 인스턴스 생성
mcp = FastMCP("서버이름")

# 도구 등록
@mcp.tool()
def my_tool():
    """도구 설명"""
    pass

# 서버 실행
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

---

## 🧮 1. 수학 서버 (Math Server)

간단한 수학 연산을 수행하는 MCP 서버입니다.

### 구현된 도구들

| 도구명     | 기능         | 입력        | 출력         |
| ---------- | ------------ | ----------- | ------------ |
| `add`      | 두 수를 더함 | a, b (정수) | a + b (정수) |
| `Subtract` | 두 수를 뺌   | a, b (정수) | a - b (정수) |

### 핵심 코드

```python
@mcp.tool()
def add(a, b) -> int:
    """더하기"""
    try:
        a = int(a)
        b = int(b)
        logging.info(f"Adding {a} and {b}")
        return a + b
    except Exception as e:
        logging.error(f"Invalid input in add: {a}, {b} - {e}")
        raise
```

### 사용 예시

✅ **성공적인 연산 결과:**

- `add(12, 4) = 16`
- `Subtract(15, 5) = 10`

---

## 🔍 2. 파일 검색 서버 (Explorer Server)

D 드라이브에서 파일명을 기준으로 키워드 검색을 수행하는 MCP 서버입니다.

### 주요 기능

- **키워드 기반 검색**: 파일명에 특정 키워드가 포함된 파일 검색
- **메타데이터 제공**: 파일 크기, 생성일, 전체 경로 정보 제공
- **대소문자 구분 없는 검색**: 사용자 편의성 향상
- **최대 결과 제한**: 검색 성능 최적화 (기본 20개)

### 핵심 코드

```python
def search_files(keyword: str, base_path: str = ROOT_DIR, max_results: int = 20) -> list[dict]:
    results = []

    for dirpath, _, filenames in os.walk(base_path):
        for fname in filenames:
            if keyword.lower() in fname.lower():
                fpath = os.path.join(dirpath, fname)
                try:
                    stat = os.stat(fpath)
                    results.append({
                        "파일명": fname,
                        "경로": fpath,
                        "크기(Bytes)": stat.st_size,
                        "생성일": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M"),
                    })
                    if len(results) >= max_results:
                        return results
                except Exception as e:
                    logging.warning(f"파일 접근 오류: {fpath} - {e}")
    return results
```

### MCP 도구 등록

```python
@mcp.tool()
def find_file(keyword: str) -> str:
    """D 드라이브에서 파일명을 기준으로 키워드에 해당하는 파일을 검색합니다."""
    logging.info(f"🔍 '{keyword}' 키워드로 파일 검색 시작")
    found = search_files(keyword)

    if not found:
        return f"'{keyword}'에 해당하는 파일을 찾을 수 없습니다."

    return "\n".join([f"📄 {f['파일명']} ({f['크기(Bytes)']} Bytes) - {f['경로']}" for f in found])
```

---

## 📚 3. RAG 시스템 서버 (RAG Server)

PDF와 Office 문서를 기반으로 한 질문응답 시스템입니다.

### 3.1 PDF 기반 RAG (main.py)

PDF 문서의 내용을 기반으로 질문에 답변하는 시스템입니다.

#### RAG 시스템 구성 요소

1. **문서 로더**: PyPDFLoader를 사용하여 PDF 파일 로드
2. **텍스트 분할**: RecursiveCharacterTextSplitter로 문서를 청크로 분할
3. **임베딩**: OpenAIEmbeddings로 텍스트를 벡터로 변환
4. **벡터 저장소**: Chroma를 사용하여 벡터 데이터 저장
5. **질문응답 체인**: RetrievalQA로 검색 기반 답변 생성

#### 핵심 코드

```python
# PDF 로드 및 분할
loader = PyPDFLoader(PDF_PATH)
pages = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = splitter.split_documents(pages)

# 임베딩 및 벡터 저장소 생성
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(docs, embeddings)

# RAG 체인 생성
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)
```

#### MCP 도구 등록

```python
@mcp.tool()
def ask_pdf(query: str) -> str:
    """PDF 내용을 기반으로 질문에 답변합니다."""
    logging.info(f"Received query: {query}")
    return qa_chain.run(query)
```

### 3.2 Office 문서 기반 RAG (office.py)

Word(.docx)와 Excel(.xlsx) 문서를 처리하는 RAG 시스템입니다.

#### 지원 문서 형식

- **Word 문서**: `.docx` 파일의 텍스트 내용 추출
- **Excel 문서**: `.xlsx` 파일의 모든 시트 데이터 텍스트화

#### 핵심 코드

```python
def load_office_documents(folder_path: str) -> list[Document]:
    docs = []

    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)

        # Word 문서 처리
        if filename.endswith(".docx"):
            word = WordDocument(path)
            full_text = "\n".join([p.text for p in word.paragraphs if p.text.strip()])
            docs.append(Document(page_content=full_text, metadata={"source": filename}))

        # Excel 문서 처리
        elif filename.endswith(".xlsx"):
            try:
                excel = pd.read_excel(path, sheet_name=None)
                for sheet_name, df in excel.items():
                    text = df.astype(str).to_string(index=False)
                    docs.append(Document(page_content=text, metadata={"source": f"{filename} - {sheet_name}"}))
            except Exception as e:
                logging.error(f"엑셀 파일 처리 오류: {filename} - {e}")

    return docs
```

#### MCP 도구 등록

```python
@mcp.tool()
def ask_office(query: str) -> str:
    """폴더 내 Word/Excel 문서를 기반으로 질문에 답변합니다."""
    logging.info(f"Query: {query}")
    try:
        return qa_chain.run(query)
    except Exception as e:
        logging.error(f"ask_office 실행 중 오류: {e}")
        return f"죄송합니다. ask_office 도구 실행 중 오류가 발생했습니다.\n[에러 내용] {e}"
```

---

## 🔐 보안 및 API 키 관리

### 보안을 고려한 API 키 관리

**최신 코드에서는 보안을 강화한 API 키 관리 방식을 사용합니다:**

```python
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
```

#### 장점

- ✅ API 키를 코드에 하드코딩하지 않음
- ✅ `.env` 파일을 통한 안전한 키 관리
- ✅ 환경별로 다른 설정 가능
- ✅ Git 등 버전 관리 시스템에 키 노출 방지

### 환경 변수 설정 방법

#### 1. .env 파일 생성 (권장)

```bash
# rag-server/.env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### 2. 시스템 환경 변수 설정

```bash
# Windows
set OPENAI_API_KEY=sk-your-actual-api-key-here

# Linux/Mac
export OPENAI_API_KEY=sk-your-actual-api-key-here
```

---

## ⚙️ 설정 및 실행

### MCP 설정 파일 (mcp.json)

```json
{
  "mcpServers": {
    "math-server": {
      "command": "C:/Python313/python.exe",
      "args": ["C:/Users/admin/test-server/math-server/math_server.py"]
    },
    "explorer-server": {
      "command": "C:/Python313/python.exe",
      "args": ["C:/Users/admin/test-server/explorer-server/main.py"]
    },
    "rag-server": {
      "command": "C:/Python313/python.exe",
      "args": ["C:/Users/admin/test-server/rag-server/main.py"]
    },
    "office-server": {
      "command": "C:/Python313/python.exe",
      "args": ["C:/Users/admin/test-server/rag-server/office.py"]
    }
  }
}
```

### 필요한 패키지

```bash
# 핵심 패키지
mcp-server-fastmcp
langchain
langchain-openai
langchain-community
chromadb
pypdf
python-dotenv
python-docx
pandas
openpyxl
```

### 설치 명령어

```bash
pip install mcp-server-fastmcp langchain langchain-openai langchain-community chromadb pypdf python-dotenv python-docx pandas openpyxl
```

---

## 🚀 사용 방법

### 1. 서버 실행

각 MCP 서버를 개별적으로 실행할 수 있습니다:

```bash
# 수학 서버
cd math-server
python math_server.py

# 파일 검색 서버
cd explorer-server
python main.py

# PDF RAG 서버
cd rag-server
python main.py

# Office RAG 서버
cd rag-server
python office.py
```

### 2. MCP 클라이언트에서 사용

Cursor, Claude Desktop 등 MCP를 지원하는 클라이언트에서 도구를 호출할 수 있습니다:

- **수학 연산**: `add(5, 3)`, `Subtract(10, 4)`
- **파일 검색**: `find_file("document")`
- **PDF 질문**: `ask_pdf("이 문서의 주요 내용은?")`
- **Office 질문**: `ask_office("엑셀 데이터에서 어떤 정보를 찾을 수 있나요?")`

---

## 📊 실습 결과 및 학습 포인트

### 성공적으로 구현된 기능

✅ MCP 서버를 통한 도구 등록 및 호출
✅ 수학 연산 도구의 정상 작동
✅ 파일 검색 시스템 구축
✅ PDF 기반 RAG 시스템 구축
✅ Office 문서 기반 RAG 시스템 구축
✅ LangChain과 MCP의 연동
✅ 보안을 고려한 API 키 관리
✅ dotenv를 통한 환경 변수 관리

### 학습된 핵심 개념

- **MCP 프로토콜**: AI와 도구 간의 표준화된 통신
- **RAG 시스템**: 검색과 생성의 결합
- **벡터 데이터베이스**: 의미적 검색을 위한 임베딩 저장
- **LangChain 체인**: 복잡한 AI 워크플로우 구성
- **보안 모범 사례**: API 키의 안전한 관리 방법
- **문서 처리**: 다양한 형식의 문서 처리 방법

---

## 🔍 문제 해결 및 디버깅

### 일반적인 문제들

| 문제                     | 원인                 | 해결 방법                                      |
| ------------------------ | -------------------- | ---------------------------------------------- |
| MCP 도구가 인식되지 않음 | 서버가 실행되지 않음 | MCP 서버 재시작                                |
| API 키 오류              | 환경 변수 미설정     | .env 파일 또는 환경 변수에 OPENAI_API_KEY 설정 |
| PDF 파일을 찾을 수 없음  | 경로 오류            | PDF_PATH 경로 확인                             |
| dotenv 관련 오류         | python-dotenv 미설치 | `pip install python-dotenv` 실행               |
| Office 문서 처리 오류    | 관련 패키지 미설치   | `pip install python-docx pandas openpyxl` 실행 |

### 로깅 활용

```python
logging.basicConfig(level=logging.INFO)
```

로그를 통해 실행 과정과 오류를 추적할 수 있습니다.

---

## 🎯 향후 발전 방향

### 단기 목표

- [ ] 웹 인터페이스 구축
- [ ] 더 많은 문서 형식 지원 (PPT, TXT 등)
- [ ] 성능 최적화 및 캐싱 구현

### 중장기 목표

- [ ] 클라우드 배포 및 확장성 개선
- [ ] 사용자 인증 및 권한 관리
- [ ] API 엔드포인트 제공
- [ ] 실시간 문서 업데이트 지원

---

## 🎉 결론

이번 실습을 통해 MCP 서버의 기본 구조와 다양한 AI 도구들의 구현 방법을 학습했습니다. 수학 연산부터 문서 처리까지 폭넓은 기능을 MCP 프로토콜을 통해 제공할 수 있게 되었습니다.

### 핵심 성과

- **MCP 프로토콜**을 통한 도구 등록 및 관리
- **LangChain**을 활용한 RAG 시스템 구축
- **다양한 문서 형식** 처리 능력 습득
- **AI 모델과 외부 도구**의 연동 방법 습득
- **보안을 고려한 API 키 관리** 방법 습득
- **실무 적용 가능한** AI 도구 개발 경험

### 실무 적용 가능성

이번 실습에서 학습한 내용은 문서 검색 시스템, 지능형 챗봇, 자동화 도구, 데이터 분석 시스템 등 다양한 AI 애플리케이션 개발에 활용할 수 있습니다.

---

## 📝 작성 정보

- **제목**: MCP 서버 실습 종합 가이드
- **작성자**: AI 어시스턴트
- **작성일**: 2024년 12월
- **실습 환경**: Windows 10, Python 3.13.7
- **사용 기술**: MCP, LangChain, OpenAI API, Chroma DB, python-dotenv
- **보안 기능**: 환경 변수를 통한 API 키 관리

---

## 🔗 관련 링크

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [LangChain 공식 문서](https://python.langchain.com/)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [Chroma DB 문서](https://docs.trychroma.com/)

---

_이 문서는 MCP 서버와 다양한 AI 도구들의 실습 과정을 종합 정리한 것입니다. 최신 코드의 보안 기능과 환경 변수 관리 방법이 반영되어 있습니다._
