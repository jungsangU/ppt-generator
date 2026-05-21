"""LLM 및 API 설정

주의: Anthropic API를 사용하지 않습니다.
로컬 LLM을 OpenAI compatible API로 호출합니다.
(예: GLM 5.1, Ollama, vLLM 등)
"""
from typing import Optional
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    """LLM 설정"""
    base_url: str
    api_key: str = "dummy"
    model_name: str = "glm-4-31b"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class DocumentConfig(BaseModel):
    """문서 파싱 설정"""
    supported_formats: list[str] = Field(default_factory=lambda: ["txt", "md", "docx", "pdf"])
    encoding: str = "utf-8"

class SlideConfig(BaseModel):
    """슬라이드 생성 설정"""
    slide_width: float = 13.333
    slide_height: float = 7.5
    font_name: str = "Calibri"
    title_font_size: int = 44
    body_font_size: int = 18

def create_llm(config: LLMConfig) -> ChatOpenAI:
    """LLM 인스턴스 생성"""
    return ChatOpenAI(
        openai_api_base=config.base_url,
        openai_api_key=config.api_key,
        model_name=config.model_name,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

# 기본 설정
DEFAULT_LLM_CONFIG = LLMConfig(
    base_url="http://localhost:8000/v1",
    api_key="dummy",
    model_name="glm-4-31b",
    temperature=0.7,
)

DEFAULT_DOCUMENT_CONFIG = DocumentConfig()
DEFAULT_SLIDE_CONFIG = SlideConfig()
