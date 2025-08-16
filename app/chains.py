from __future__ import annotations

from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


_llm: Optional[BaseChatModel] = None


def set_llm(llm: BaseChatModel) -> None:
    global _llm
    _llm = llm


def run_chain(user_text: str, brand: str) -> str:
    if _llm is None:
        raise RuntimeError("LLM not initialized. Call set_llm() first.")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres un asistente de WhatsApp para {brand}. Responde claro, breve y útil. Responde en el mismo idioma del usuario si es posible.",
            ),
            ("human", "{input}"),
        ]
    )

    chain = prompt | _llm | StrOutputParser()
    return chain.invoke({"input": user_text, "brand": brand})


