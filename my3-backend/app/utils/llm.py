from langchain_openai import ChatOpenAI
from app.config import settings


def get_llm(temperature: float = 0.7):
    """Get configured OpenAI LLM instance."""
    return ChatOpenAI(
        model="gpt-4",
        temperature=temperature,
        api_key=settings.openai_api_key
    )

