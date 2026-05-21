#!/usr/bin/env python3
"""
Langchain 기반 문서 → PPT 변환 파이프라인 사용 예시

사용법:
    python3 example_langchain_pipeline.py --input input.txt --output output.pptx --url http://localhost:8000/v1

또는 Python 코드에서:
    from ppt_generator.methods.langchain_pipeline import DocumentToPPTPipeline, LLMConfig

    config = LLMConfig(
        base_url="http://localhost:8000/v1",
        api_key="dummy",
        model_name="glm-4-31b"
    )
    pipeline = DocumentToPPTPipeline(llm_config=config, theme="professional")
    pipeline.run("input.txt", "output.pptx", num_slides=10)
"""

import argparse
from pathlib import Path

from ppt_generator.methods.langchain_pipeline import DocumentToPPTPipeline, LLMConfig


def create_sample_document(file_path: str) -> None:
    """샘플 문서 생성"""
    sample_content = """
    인공지능(AI)의 미래

    인공지능은 현대 사회의 가장 중요한 기술 중 하나가 되었습니다.

    1. 머신러닝의 발전
    - 신경망 기술의 획기적인 발전
    - 대규모 데이터 처리 능력 증대
    - 실시간 의사결정 시스템 구축

    2. 자연어 처리 기술
    - 텍스트 이해 및 생성 기술
    - 다중 언어 지원
    - 문맥을 고려한 답변 생성

    3. 컴퓨터 비전
    - 이미지 인식 및 분석
    - 실시간 객체 추적
    - 자동 이미지 생성

    4. AI의 실제 응용 분야
    - 의료: 질병 진단 및 치료 계획
    - 금융: 위험 평가 및 거래 최적화
    - 교육: 개인화된 학습 경험 제공
    - 제조: 품질 관리 및 생산성 향상

    5. 향후 전망
    - 더욱 효율적인 알고리즘 개발
    - 윤리적 AI 구현
    - 인간과 AI의 협력 강화
    """

    Path(file_path).write_text(sample_content)
    print(f"샘플 문서 생성: {file_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Langchain 기반 문서 → PPT 변환"
    )
    parser.add_argument("--input", default="sample_input.txt", help="입력 문서 경로")
    parser.add_argument("--output", default="output_langchain.pptx", help="출력 PPT 경로")
    parser.add_argument("--url", default="http://localhost:8000/v1", help="로컬 LLM baseurl")
    parser.add_argument("--model", default="glm-4-31b", help="LLM 모델명")
    parser.add_argument("--slides", type=int, default=8, help="슬라이드 개수")
    parser.add_argument("--theme", default="blue", help="테마 (blue, professional, modern)")
    parser.add_argument("--create-sample", action="store_true", help="샘플 문서 생성")

    args = parser.parse_args()

    # 샘플 문서 생성
    if args.create_sample:
        create_sample_document(args.input)

    # LLM 설정
    llm_config = LLMConfig(
        base_url=args.url,
        api_key="dummy",
        model_name=args.model,
        temperature=0.7
    )

    # 파이프라인 실행
    pipeline = DocumentToPPTPipeline(
        llm_config=llm_config,
        theme=args.theme
    )

    try:
        pipeline.run(
            input_path=args.input,
            output_path=args.output,
            num_slides=args.slides,
            apply_validation=True
        )
    except FileNotFoundError:
        print(f"오류: 입력 파일을 찾을 수 없습니다 ({args.input})")
        print(f"--create-sample 옵션으로 샘플 파일을 생성할 수 있습니다")
        return 1
    except Exception as e:
        print(f"오류: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
