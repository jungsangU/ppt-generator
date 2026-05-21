"""Task 3: 슬라이드 레이아웃 계획"""
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pydantic import BaseModel

class LayoutConfig(BaseModel):
    """슬라이드 레이아웃 설정"""
    slide_number: int
    title: str
    layout_type: str  # single_column, two_column, bullet_list, image, quote
    text_alignment: str = "left"  # left, center, right
    has_image: bool = False
    image_position: str = "right"  # right, bottom, none

class LayoutPlan(BaseModel):
    """레이아웃 계획"""
    layouts: list[LayoutConfig]

class LayoutPlanner:
    """슬라이드 레이아웃 계획"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

        self.layout_prompt = PromptTemplate(
            input_variables=["outline"],
            template="""다음 아웃라인에 대해 각 슬라이드의 최적 레이아웃을 계획해줘.

아웃라인:
{outline}

요구사항:
1. 슬라이드 유형에 맞는 레이아웃 선택:
   - 타이틀 슬라이드: 중앙 정렬
   - 콘텐츠 슬라이드: bullet_list 또는 two_column
   - 닫기 슬라이드: 중앙 정렬
2. 포인트가 많으면 two_column으로 분산
3. 필요하면 이미지 영역 예약

JSON 형식:
{{
    "layouts": [
        {{"slide_number": 1, "title": "...", "layout_type": "center_title", "text_alignment": "center", "has_image": false}},
        {{"slide_number": 2, "title": "...", "layout_type": "bullet_list", "text_alignment": "left", "has_image": false}},
        ...
    ]
}}"""
        )
        self.layout_chain = LLMChain(
            llm=self.llm,
            prompt=self.layout_prompt
        )

    def plan(self, outline: str) -> LayoutPlan:
        """레이아웃 계획 수립"""
        result = self.layout_chain.run(outline=outline)
        return self._parse_layout_plan(result)

    def _parse_layout_plan(self, result: str) -> LayoutPlan:
        """레이아웃 계획 파싱"""
        try:
            json_start = result.find("{")
            json_end = result.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                return self._create_default_layout_plan()

            json_str = result[json_start:json_end]
            data = json.loads(json_str)

            layouts = []
            for layout_data in data.get("layouts", []):
                layouts.append(LayoutConfig(
                    slide_number=layout_data["slide_number"],
                    title=layout_data.get("title", ""),
                    layout_type=layout_data.get("layout_type", "bullet_list"),
                    text_alignment=layout_data.get("text_alignment", "left"),
                    has_image=layout_data.get("has_image", False),
                    image_position=layout_data.get("image_position", "right")
                ))

            return LayoutPlan(layouts=layouts)
        except (json.JSONDecodeError, KeyError):
            # 기본값으로 반환
            return self._create_default_layout_plan()

    def _create_default_layout_plan(self) -> LayoutPlan:
        """기본 레이아웃 계획"""
        layouts = [
            LayoutConfig(
                slide_number=1,
                title="프레젠테이션",
                layout_type="center_title",
                text_alignment="center"
            ),
            LayoutConfig(
                slide_number=2,
                title="주요 내용",
                layout_type="bullet_list",
                text_alignment="left"
            ),
        ]
        return LayoutPlan(layouts=layouts)
