import os
from typing import Any, Optional

from langchain_core.runnables import RunnableWithFallbacks

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None


def create_model_with_fallback(
    primary_model: str = "gemini-2.0-flash",
    fallback_groq_model: str = "llama-3.3-70b-versatile",
    fallback_openrouter_model: str = "anthropic/claude-3.5-sonnet",
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> RunnableWithFallbacks:
    """Create a model with automatic fallback chain.

    Tries Gemini first, then Groq, then OpenRouter on failure.

    Args:
        primary_model: Gemini model name (default: gemini-2.0-flash)
        fallback_groq_model: Groq model name (default: llama-3.3-70b-versatile)
        fallback_openrouter_model: OpenRouter model name (default: anthropic/claude-3.5-sonnet)
        temperature: Model temperature (default: 0.7)
        max_tokens: Max tokens to generate (default: 4096)

    Returns:
        RunnableWithFallbacks chain
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    runnables = []

    if gemini_key and ChatGoogleGenerativeAI:
        try:
            primary = ChatGoogleGenerativeAI(
                model=primary_model,
                google_api_key=gemini_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            runnables.append(primary)
        except Exception:
            pass

    if groq_key and ChatGroq:
        try:
            fallback_groq = ChatGroq(
                model=fallback_groq_model,
                groq_api_key=groq_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            runnables.append(fallback_groq)
        except Exception:
            pass

    if openrouter_key and ChatOpenAI:
        try:
            fallback_or = ChatOpenAI(
                model=fallback_openrouter_model,
                openai_api_key=openrouter_key,
                temperature=temperature,
                max_tokens=max_tokens,
                base_url="https://openrouter.ai/api/v1",
            )
            runnables.append(fallback_or)
        except Exception:
            pass

    if not runnables:
        raise ValueError("No API keys available for any model")

    if len(runnables) == 1:
        return runnables[0]

    chain = runnables[0]
    for fallback in runnables[1:]:
        chain = chain.with_fallbacks([fallback])

    return chain
