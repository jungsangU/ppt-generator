# Langchain 기반 문서 → PPT 변환 파이프라인

로컬 LLM(GLM 5.1 등)을 사용하여 문서를 PowerPoint 프레젠테이션으로 자동 변환하는 파이프라인입니다.

## 아키텍처

1단계부터 7단계까지 단계별로 처리됩니다:

```
입력 문서
    ↓
[Task 1] 콘텐츠 추출 & 분석 (LLM) → ExtractedContent
    ↓
[Task 2] 아웃라인 생성 (LLM) → Outline (슬라이드 구조)
    ↓
[Task 3] 슬라이드 레이아웃 계획 (LLM) → LayoutPlan
    ↓
[Task 4] 슬라이드 콘텐츠 생성 (LLM) → ContentPlan
    ↓
[Task 5] PPT 생성 (python-pptx) → Presentation
    ↓
[Task 6] 디자인 & 스타일링 (Design) → Styled PPT
    ↓
[Task 7] 검증 & 내보내기 (LLM 검증) → PPT 파일 저장
    ↓
출력 PPT
```

## 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# 필수 패키지
pip install langchain>=0.1.0 python-docx pdfplumber pydantic
```

## 사용 방법

### 1. Python 코드에서 사용

```python
from ppt_generator.methods.langchain_pipeline import DocumentToPPTPipeline, LLMConfig

# LLM 설정 (로컬 GLM 5.1 예시)
config = LLMConfig(
    base_url="http://localhost:8000/v1",  # 로컬 LLM 주소
    api_key="dummy",
    model_name="glm-4-31b"
)

# 파이프라인 생성
pipeline = DocumentToPPTPipeline(
    llm_config=config,
    theme="professional"  # blue, professional, modern
)

# 실행
pipeline.run(
    input_path="document.txt",
    output_path="presentation.pptx",
    num_slides=10,
    apply_validation=True
)
```

### 2. CLI에서 사용

```bash
# 샘플 문서 생성 및 실행
python3 example_langchain_pipeline.py --create-sample

# 커스텀 설정으로 실행
python3 example_langchain_pipeline.py \
    --input my_document.txt \
    --output my_presentation.pptx \
    --url http://localhost:8000/v1 \
    --slides 12 \
    --theme professional
```

## 지원 파일 형식

- **텍스트**: `.txt`
- **마크다운**: `.md`
- **Word**: `.docx` (python-docx 필요)
- **PDF**: `.pdf` (pdfplumber 필요)

## 주요 모듈

### config.py
- LLM 설정
- `LLMConfig`: LLM 파라미터 정의
- `create_llm()`: ChatOpenAI 인스턴스 생성

### parsers/document_parser.py (Task 1)
- 다양한 형식의 문서 파싱
- LLM을 사용하여 핵심 콘텐츠 추출
- 제목, 요약, 주요 포인트 추출

### chains/outline_generator.py (Task 2)
- 콘텐츠를 슬라이드 아웃라인으로 변환
- 각 슬라이드 제목과 불릿 포인트 생성
- JSON 형식의 구조화된 아웃라인

### chains/layout_planner.py (Task 3)
- 각 슬라이드의 최적 레이아웃 결정
- 콘텐츠 양에 따른 레이아웃 분배
- 이미지 영역 예약 등

### chains/content_generator.py (Task 4)
- 각 슬라이드의 상세 콘텐츠 생성
- 발표자 노트 생성
- 전문적이고 매력적인 표현 작성

### builders/ppt_builder.py (Task 5)
- python-pptx를 사용한 PPT 생성
- 타이틀, 콘텐츠, 마무리 슬라이드
- 단일/2단 레이아웃 지원

### builders/designer.py (Task 6)
- 디자인 테마 적용
- 색상 팔레트 관리
- 푸터 추가 등 스타일링

### validators/validator.py (Task 7)
- LLM을 사용한 콘텐츠 품질 검증
- 일관성, 명확성, 문법 확인
- 품질 점수 및 개선 제안

### pipeline.py
- 1~7단계 전체 오케스트레이션
- 단계별 진행 상황 출력
- 최종 PPT 파일 생성

## 테마

세 가지 기본 테마 제공:

- **blue**: 전문적인 파란색 테마
- **professional**: 비즈니스 스타일
- **modern**: 모던한 스타일

각 테마는 색상 팔레트가 다릅니다.

## 성능 최적화

### LLM 호출 최소화
- Task 1, 2, 4에서만 LLM 호출
- Task 3, 5, 6, 7에서는 규칙 기반 처리
- 빠른 생성 가능

### 메모리 사용
- 대용량 문서는 자동으로 자르기
- 각 단계별 중간 결과는 메모리에만 유지
- 최종 PPT만 디스크에 저장

## 트러블슈팅

### "OpenAI API 연결 실패"
→ baseurl이 올바르고 LLM 서버가 실행 중인지 확인

### "JSON 파싱 오류"
→ LLM 응답 형식이 예상과 다를 때. 기본값으로 폴백됨

### "파일 형식 미지원"
→ 지원하는 형식: txt, md, docx, pdf
→ docx, pdf는 추가 패키지 설치 필요

## 커스터마이징

### LLM 파라미터 조정
```python
config = LLMConfig(
    base_url="http://localhost:8000/v1",
    api_key="dummy",
    model_name="glm-4-31b",
    temperature=0.5,  # 낮을수록 정확함
    max_tokens=2000
)
```

### 슬라이드 스타일 커스터마이징
`builders/ppt_builder.py`에서 폰트, 크기, 색상 수정 가능

### 프롬프트 커스터마이징
각 `chains/` 파일의 `PromptTemplate`을 수정하여 LLM 입력 변경 가능

## 라이선스

이 프로젝트는 PPT Generator의 일부입니다.

## 개발자 가이드

### 새로운 Task 추가
1. `chains/` 또는 `validators/` 디렉토리에 새로운 파일 생성
2. 해당 클래스 작성
3. `pipeline.py`의 `run()` 메서드에 단계 추가

### 새로운 테마 추가
`builders/designer.py`의 `THEMES` 딕셔너리에 추가:
```python
THEMES = {
    "custom": ColorTheme(
        primary=(r, g, b),
        secondary=(r, g, b),
        accent=(r, g, b),
        text_dark=(r, g, b),
        text_light=(r, g, b)
    )
}
```

### 테스트
```bash
python3 example_langchain_pipeline.py --create-sample --theme professional
```
