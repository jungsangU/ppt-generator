"""Task 7: 검증 & 내보내기"""
from pptx import Presentation
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pydantic import BaseModel, Field

class ValidationResult(BaseModel):
    """검증 결과"""
    is_valid: bool
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    quality_score: float = 0.0

class ContentValidator:
    """프레젠테이션 검증"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

        self.validation_prompt = PromptTemplate(
            input_variables=["content"],
            template="""다음 프레젠테이션 콘텐츠를 검증해줘.

콘텐츠:
{content}

검증 항목:
1. 콘텐츠의 일관성 확인
2. 각 슬라이드의 명확성 확인
3. 타이포 또는 문법 오류 확인
4. 논리적 흐름 확인

결과 형식:
문제점: [있으면 나열, 없으면 "없음"]
개선사항: [개선 가능한 항목들]
품질점수: [0-100]"""
        )
        self.validation_chain = LLMChain(
            llm=self.llm,
            prompt=self.validation_prompt
        )

    def validate_presentation(self, prs: Presentation) -> ValidationResult:
        """프레젠테이션 검증"""
        content = self._extract_presentation_content(prs)
        return self._validate_content(content)

    def validate_content_text(self, content: str) -> ValidationResult:
        """텍스트 콘텐츠 검증"""
        return self._validate_content(content)

    def _validate_content(self, content: str) -> ValidationResult:
        """콘텐츠 검증"""
        result = self.validation_chain.run(content=content)
        return self._parse_validation_result(result)

    def _extract_presentation_content(self, prs: Presentation) -> str:
        """프레젠테이션에서 콘텐츠 추출"""
        content = ""
        for i, slide in enumerate(prs.slides):
            content += f"\n슬라이드 {i + 1}:\n"
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    content += shape.text + "\n"
        return content

    def _parse_validation_result(self, result: str) -> ValidationResult:
        """검증 결과 파싱"""
        lines = result.strip().split("\n")

        issues = []
        suggestions = []
        quality_score = 80.0

        for line in lines:
            if line.startswith("문제점:"):
                problems = line.replace("문제점:", "").strip()
                if problems != "없음":
                    issues = [p.strip() for p in problems.split(",")]
            elif line.startswith("개선사항:"):
                sugg = line.replace("개선사항:", "").strip()
                suggestions = [s.strip() for s in sugg.split(",")]
            elif line.startswith("품질점수:"):
                try:
                    score_str = line.replace("품질점수:", "").strip()
                    quality_score = float(score_str)
                except ValueError:
                    quality_score = 75.0

        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            suggestions=suggestions,
            quality_score=quality_score
        )

    def print_validation_report(self, result: ValidationResult) -> None:
        """검증 리포트 출력"""
        print("\n" + "="*50)
        print("프레젠테이션 검증 리포트")
        print("="*50)

        print(f"\n상태: {'✓ 통과' if result.is_valid else '✗ 개선 필요'}")
        print(f"품질점수: {result.quality_score:.1f}/100")

        if result.issues:
            print("\n문제점:")
            for issue in result.issues:
                print(f"  - {issue}")

        if result.suggestions:
            print("\n개선 사항:")
            for sugg in result.suggestions:
                print(f"  - {sugg}")

        print("\n" + "="*50 + "\n")
