"""Task 4: 슬라이드 콘텐츠 생성"""
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pydantic import BaseModel

class SlideContent(BaseModel):
    """슬라이드 콘텐츠"""
    slide_number: int
    title: str
    content: list[str]  # 텍스트 또는 불릿 포인트
    notes: str = ""  # 발표자 노트

class ContentPlan(BaseModel):
    """콘텐츠 계획"""
    slides: list[SlideContent]

class ContentGenerator:
    """슬라이드 콘텐츠 생성"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

        self.content_prompt = PromptTemplate(
            input_variables=["outline", "slide_info"],
            template="""다음 아웃라인과 슬라이드 정보에 따라 슬라이드 콘텐츠를 생성해줘.

아웃라인:
{outline}

슬라이드 정보:
{slide_info}

요구사항:
1. 각 슬라이드마다 명확하고 간결한 콘텐츠 작성
2. 불릿 포인트는 3-5개, 각각 한 줄
3. 전문적이고 매력적인 표현 사용
4. 타이틀 슬라이드: 제목만
5. 마무리 슬라이드: "감사합니다" 또는 마무리 메시지

JSON 형식:
{{
    "slides": [
        {{"slide_number": 1, "title": "...", "content": [], "notes": ""}},
        {{"slide_number": 2, "title": "...", "content": ["...", "...", "..."], "notes": "발표자 노트"}},
        ...
    ]
}}"""
        )
        self.content_chain = LLMChain(
            llm=self.llm,
            prompt=self.content_prompt
        )

    def generate(self, outline: str, slide_info: str = "") -> ContentPlan:
        """슬라이드 콘텐츠 생성"""
        result = self.content_chain.run(
            outline=outline,
            slide_info=slide_info
        )
        return self._parse_content_plan(result)

    def _parse_content_plan(self, result: str) -> ContentPlan:
        """콘텐츠 계획 파싱"""
        try:
            json_start = result.find("{")
            json_end = result.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                return self._create_default_content_plan()

            json_str = result[json_start:json_end]
            data = json.loads(json_str)

            slides = []
            for slide_data in data.get("slides", []):
                slides.append(SlideContent(
                    slide_number=slide_data["slide_number"],
                    title=slide_data.get("title", ""),
                    content=slide_data.get("content", []),
                    notes=slide_data.get("notes", "")
                ))

            return ContentPlan(slides=slides)
        except (json.JSONDecodeError, KeyError):
            return self._create_default_content_plan()

    def _create_default_content_plan(self) -> ContentPlan:
        """기본 콘텐츠 계획"""
        slides = [
            SlideContent(
                slide_number=1,
                title="프레젠테이션",
                content=[]
            ),
            SlideContent(
                slide_number=2,
                title="주요 내용",
                content=["포인트 1", "포인트 2", "포인트 3"]
            ),
            SlideContent(
                slide_number=3,
                title="감사합니다",
                content=[]
            ),
        ]
        return ContentPlan(slides=slides)
