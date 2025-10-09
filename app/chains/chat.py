from __future__ import annotations

from typing import Dict, Any

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.utils.config import settings


# Build the core prompt. The companion persona variables are fed in via partials
SYSTEM_TEMPLATE = (
    "You are an AI companion. Adopt the given persona.\n"
    "Name: {name}\nAge: {age}\nGender: {gender}\nBirth country: {birth_country}\n"
    "Personality: {personality}\nEducation: {education}\nBackground: {background}\n\n"
    "Speak concisely and empathetically. Remember key facts about the user across turns."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_TEMPLATE),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

# Message history factory using SQLite via LangChain community package

def build_chain_with_memory(session_id: str, persona_vars: Dict[str, Any]) -> RunnableWithMessageHistory:
    """Wrap the chat chain with SQL-based message history keyed by session_id."""

    def get_history(_: Dict[str, Any]) -> BaseChatMessageHistory:
        # SQLChatMessageHistory creates a table 'message_store' in the provided DB URL by default
        return SQLChatMessageHistory(session_id=session_id, connection_string=settings.database_url)

    # Lazily construct the LLM and chain so imports don't require API keys
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set. Please configure it in your environment.")

    llm = ChatOpenAI(
        model=settings.model_name,
        temperature=settings.temperature,
        api_key=settings.openai_api_key,
    )

    chain = prompt | llm

    runnable = RunnableWithMessageHistory(
        chain,
        get_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    # Bind persona variables via partials so they are available in the prompt
    return runnable.with_config(configurable={"thread_id": session_id}).partial(**persona_vars)
