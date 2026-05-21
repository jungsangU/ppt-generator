"""메인 파이프라인: 1~7단계 통합"""
from typing import Optional
from langchain.chat_models import ChatOpenAI

from .config import LLMConfig, create_llm
from .parsers import DocumentParser
from .chains import OutlineGenerator, LayoutPlanner, ContentGenerator
from .builders import PPTBuilder, DesignApplier
from .validators import ContentValidator

class DocumentToPPTPipeline:
    """문서 → PPT 변환 파이프라인"""

    def __init__(self, llm_config: Optional[LLMConfig] = None, theme: str = "blue"):
        # LLM 초기화
        if llm_config is None:
            from .config import DEFAULT_LLM_CONFIG
            llm_config = DEFAULT_LLM_CONFIG

        self.llm_config = llm_config
        self.llm = create_llm(llm_config)
        self.theme = theme

        # Task별 모듈 초기화
        self.parser = DocumentParser(self.llm)
        self.outline_generator = OutlineGenerator(self.llm)
        self.layout_planner = LayoutPlanner(self.llm)
        self.content_generator = ContentGenerator(self.llm)
        self.validator = ContentValidator(self.llm)

    def run(
        self,
        input_path: str,
        output_path: str,
        num_slides: int = 8,
        apply_validation: bool = True
    ) -> str:
        """
        전체 파이프라인 실행

        Args:
            input_path: 입력 문서 경로
            output_path: 출력 PPT 경로
            num_slides: 생성할 슬라이드 개수
            apply_validation: 검증 수행 여부

        Returns:
            생성된 PPT 경로
        """
        print("\n" + "="*50)
        print("문서 → PPT 변환 파이프라인 시작")
        print("="*50)

        # Task 1: 콘텐츠 추출 & 분석
        print("\n[Task 1/7] 콘텐츠 추출 & 분석 중...")
        extracted_content = self.parser.parse_file(input_path)
        print(f"✓ 제목: {extracted_content.title}")
        print(f"✓ 요약: {extracted_content.summary[:100]}...")

        # Task 2: 아웃라인 생성
        print("\n[Task 2/7] 아웃라인 생성 중...")
        outline = self.outline_generator.generate(
            content=extracted_content.summary,
            num_slides=num_slides
        )
        print(f"✓ {outline.total_slides}개 슬라이드 계획 완료")

        # Task 3: 슬라이드 레이아웃 계획
        print("\n[Task 3/7] 슬라이드 레이아웃 계획 중...")
        layout_plan = self.layout_planner.plan(
            outline=outline.model_dump_json()
        )
        print(f"✓ {len(layout_plan.layouts)}개 슬라이드 레이아웃 설정")

        # Task 4: 슬라이드 콘텐츠 생성
        print("\n[Task 4/7] 슬라이드 콘텐츠 생성 중...")
        content_plan = self.content_generator.generate(
            outline=outline.model_dump_json(),
            slide_info=layout_plan.model_dump_json()
        )
        print(f"✓ {len(content_plan.slides)}개 슬라이드 콘텐츠 준비 완료")

        # Task 5: PPT 생성
        print("\n[Task 5/7] PPT 생성 중...")
        ppt_builder = PPTBuilder(
            title=extracted_content.title
        )
        self._build_presentation(ppt_builder, content_plan)
        print(f"✓ PPT 슬라이드 생성 완료")

        # Task 6: 디자인 & 스타일링
        print("\n[Task 6/7] 디자인 & 스타일링 적용 중...")
        designer = DesignApplier(ppt_builder.prs, theme=self.theme)
        designer.apply_theme()
        designer.add_footer(text=extracted_content.title)
        print(f"✓ 테마 '{self.theme}' 적용 완료")

        # Task 7: 검증 & 내보내기
        print("\n[Task 7/7] 검증 & 저장 중...")
        if apply_validation:
            validation_result = self.validator.validate_presentation(ppt_builder.prs)
            self.validator.print_validation_report(validation_result)

        ppt_builder.save(output_path)
        print(f"✓ PPT 저장 완료: {output_path}")

        print("\n" + "="*50)
        print("✓ 파이프라인 완료!")
        print("="*50 + "\n")

        return output_path

    def _build_presentation(self, ppt_builder: PPTBuilder, content_plan) -> None:
        """프레젠테이션 구성"""
        for slide in content_plan.slides:
            if slide.type == "title":
                ppt_builder.add_title_slide(slide.title)
            elif slide.type == "closing":
                ppt_builder.add_closing_slide(slide.title)
            else:
                # content 슬라이드
                layout_type = "bullet"
                if len(slide.content) > 6:
                    layout_type = "two_column"

                ppt_builder.add_content_slide(
                    title=slide.title,
                    content=slide.content,
                    layout_type=layout_type
                )
