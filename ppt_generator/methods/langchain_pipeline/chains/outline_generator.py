"""Task 2: 아웃라인 생성"""
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pydantic import BaseModel, Field

class Slide(BaseModel):
    """슬라이드 정보"""
    slide_number: int
    title: str
    type: str = "content"  # title, content, section, closing
    bullet_points: list[str] = Field(default_factory=list)

class Outline(BaseModel):
    """프레젠테이션 아웃라인"""
    title: str
    total_slides: int
    slides: list[Slide]

class OutlineGenerator:
    """프레젠테이션 아웃라인 생성"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

        self.outline_prompt = PromptTemplate(
            input_variables=["content", "num_slides"],
            template="""다음 내용을 {num_slides}개의 슬라이드로 구성할 아웃라인을 만들어줘.

내용:
{content}

요구사항:
1. 첫 번째는 타이틀 슬라이드 (제목만)
2. 마지막은 마무리 슬라이드
3. 나머지는 콘텐츠 슬라이드
4. 각 슬라이드에 제목과 주요 포인트 포함

JSON 형식으로 답변해줘:
{{
    "title": "프레젠테이션 제목",
    "slides": [
        {{"slide_number": 1, "title": "...", "type": "title", "bullet_points": []}},
        {{"slide_number": 2, "title": "...", "type": "content", "bullet_points": ["...", "..."]}},
        ...
    ]
}}"""
        )
        self.outline_chain = LLMChain(
            llm=self.llm,
            prompt=self.outline_prompt
        )

    def generate(self, content: str, num_slides: int = 8) -> Outline:
        """아웃라인 생성"""
        result = self.outline_chain.run(
            content=content,
            num_slides=num_slides
        )

        return self._parse_outline(result)

    def _parse_outline(self, result: str) -> Outline:
        """아웃라인 파싱"""
        try:
            # JSON 추출
            json_start = result.find("{")
            json_end = result.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                return self._create_default_outline(result)

            json_str = result[json_start:json_end]
            data = json.loads(json_str)

            slides = []
            for slide_data in data.get("slides", []):
                slides.append(Slide(
                    slide_number=slide_data["slide_number"],
                    title=slide_data.get("title", ""),
                    type=slide_data.get("type", "content"),
                    bullet_points=slide_data.get("bullet_points", [])
                ))

            return Outline(
                title=data.get("title", "프레젠테이션"),
                total_slides=len(slides),
                slides=slides
            )
        except (json.JSONDecodeError, KeyError) as e:
            # 파싱 실패 시 기본값으로 생성
            return self._create_default_outline(result)

    def _create_default_outline(self, content: str) -> Outline:
        """기본 아웃라인 생성"""
        slides = [
            Slide(slide_number=1, title="프레젠테이션", type="title"),
            Slide(
                slide_number=2,
                title="주요 내용",
                type="content",
                bullet_points=content.split("\n")[:5]
            ),
            Slide(slide_number=3, title="감사합니다", type="closing"),
        ]

        return Outline(
            title="프레젠테이션",
            total_slides=len(slides),
            slides=slides
        )
