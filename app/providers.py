from __future__ import annotations

import os
from langchain_core.language_models.chat_models import BaseChatModel


def build_llm() -> BaseChatModel:
    """Build a chat LLM based on environment variables.

    Reads PROVIDER in {"gemini", "openai"} and constructs the appropriate
    LangChain chat model with default temperature 0.4.
    """
    provider = (os.getenv("PROVIDER") or "").strip().lower()
    temperature = float(os.getenv("TEMPERATURE", "0.4"))

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set")
        return ChatGoogleGenerativeAI(
            model=model, temperature=temperature, google_api_key=api_key
        )

    raise ValueError("Invalid PROVIDER. Use 'gemini' or 'openai'.")


