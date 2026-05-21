"""Task 1: 콘텐츠 추출 & 분석"""
from pathlib import Path
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pydantic import BaseModel

try:
    from python_docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

class ExtractedContent(BaseModel):
    """추출된 콘텐츠"""
    title: str
    summary: str
    main_points: list[str]
    raw_text: str

class DocumentParser:
    """문서 파싱 및 콘텐츠 추출"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

        # LLM Chain for content extraction
        self.extraction_prompt = PromptTemplate(
            input_variables=["document_text"],
            template="""다음 문서에서 다음 정보를 추출해줘:
1. 문서의 주제/제목 (한 줄)
2. 전체 내용 요약 (3-5줄)
3. 주요 포인트 5-7개 (각각 한 줄씩)

문서:
{document_text}

답변 형식:
제목: [제목]
요약: [요약]
주요 포인트:
- [포인트1]
- [포인트2]
- [포인트3]
..."""
        )
        self.extraction_chain = LLMChain(
            llm=self.llm,
            prompt=self.extraction_prompt
        )

    def parse_file(self, file_path: str) -> ExtractedContent:
        """파일에서 콘텐츠 추출"""
        file_ext = Path(file_path).suffix.lower()

        if file_ext == ".txt":
            text = self._read_text_file(file_path)
        elif file_ext == ".md":
            text = self._read_markdown_file(file_path)
        elif file_ext == ".docx":
            text = self._read_docx_file(file_path)
        elif file_ext == ".pdf":
            text = self._read_pdf_file(file_path)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {file_ext}")

        return self.parse_text(text)

    def parse_text(self, text: str) -> ExtractedContent:
        """텍스트에서 콘텐츠 추출"""
        # 긴 텍스트는 자르기
        if len(text) > 3000:
            text = text[:3000]

        # LLM으로 콘텐츠 추출
        result = self.extraction_chain.run(document_text=text)

        # 결과 파싱
        return self._parse_extraction_result(result, text)

    def _read_text_file(self, file_path: str) -> str:
        """텍스트 파일 읽기"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _read_markdown_file(self, file_path: str) -> str:
        """마크다운 파일 읽기"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _read_docx_file(self, file_path: str) -> str:
        """DOCX 파일 읽기"""
        if DocxDocument is None:
            raise ImportError("python-docx가 필요합니다: pip install python-docx")

        doc = DocxDocument(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _read_pdf_file(self, file_path: str) -> str:
        """PDF 파일 읽기"""
        if pdfplumber is None:
            raise ImportError("pdfplumber가 필요합니다: pip install pdfplumber")

        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _parse_extraction_result(self, result: str, raw_text: str) -> ExtractedContent:
        """추출 결과 파싱"""
        lines = result.strip().split("\n")

        title = ""
        summary = ""
        main_points = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("제목:"):
                title = line.replace("제목:", "").strip()
            elif line.startswith("요약:"):
                summary = line.replace("요약:", "").strip()
            elif line.startswith("주요 포인트:"):
                continue
            elif line.startswith("- "):
                main_points.append(line[2:].strip())

        return ExtractedContent(
            title=title or "제목 없음",
            summary=summary or result[:200],
            main_points=main_points if main_points else [result[:100]],
            raw_text=raw_text
        )
