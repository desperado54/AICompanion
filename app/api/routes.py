from __future__ import annotations

from typing import Any, Dict

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.utils.db import session_scope
from app.models import User, Companion, Conversation
from app.chains.chat import build_chain_with_memory

api = Blueprint("api", __name__)


# Helpers

def get_json() -> Dict[str, Any]:
    if not request.is_json:
        return {}
    return request.get_json(force=True) or {}


@api.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok"})


# Users
@api.route("/users", methods=["POST"])
def create_user() -> Any:
    payload = get_json()
    username = (payload.get("username") or "").strip()
    if not username:
        return jsonify({"error": "username is required"}), 400

    with session_scope() as db:
        if db.scalar(select(User).where(User.username == username)):
            return jsonify({"error": "username already exists"}), 409
        user = User(username=username)
        db.add(user)
        db.flush()
        return jsonify({"id": user.id, "username": user.username}), 201


@api.route("/users", methods=["GET"])
def list_users() -> Any:
    with session_scope() as db:
        users = db.scalars(select(User)).all()
        return jsonify([
            {"id": u.id, "username": u.username, "created_at": u.created_at.isoformat()} for u in users
        ])


# Companions
@api.route("/companions", methods=["POST"])
def create_companion() -> Any:
    payload = get_json()

    user_id = payload.get("user_id")
    name = (payload.get("name") or "").strip()
    if not user_id or not name:
        return jsonify({"error": "user_id and name are required"}), 400

    attrs = {
        "age": payload.get("age"),
        "gender": payload.get("gender"),
        "birth_country": payload.get("birth_country"),
        "personality": payload.get("personality"),
        "education": payload.get("education"),
        "background": payload.get("background"),
        "system_prompt": payload.get("system_prompt"),
    }

    with session_scope() as db:
        if not db.get(User, user_id):
            return jsonify({"error": "user not found"}), 404

        companion = Companion(user_id=user_id, name=name, **attrs)
        db.add(companion)
        db.flush()
        return jsonify({"id": companion.id, "name": companion.name}), 201


@api.route("/companions", methods=["GET"])
def list_companions() -> Any:
    user_id = request.args.get("user_id", type=int)
    with session_scope() as db:
        stmt = select(Companion)
        if user_id:
            stmt = stmt.where(Companion.user_id == user_id)
        companions = db.scalars(stmt).all()
        return jsonify([
            {
                "id": c.id,
                "user_id": c.user_id,
                "name": c.name,
                "age": c.age,
                "gender": c.gender,
                "birth_country": c.birth_country,
                "personality": c.personality,
                "education": c.education,
                "background": c.background,
                "system_prompt": c.system_prompt,
            }
            for c in companions
        ])


@api.route("/companions/<int:companion_id>", methods=["PATCH"])
def update_companion(companion_id: int) -> Any:
    payload = get_json()
    allowed = {
        "name", "age", "gender", "birth_country", "personality", "education", "background", "system_prompt"
    }
    updates = {k: v for k, v in payload.items() if k in allowed}

    with session_scope() as db:
        companion = db.get(Companion, companion_id)
        if not companion:
            return jsonify({"error": "companion not found"}), 404
        for k, v in updates.items():
            setattr(companion, k, v)
        db.add(companion)
        db.flush()
        return jsonify({"id": companion.id, "updated": True})


# Conversations
@api.route("/conversations", methods=["POST"])
def create_conversation() -> Any:
    payload = get_json()
    user_id = payload.get("user_id")
    companion_id = payload.get("companion_id")
    session_key = payload.get("session_key")
    if not user_id or not companion_id or not session_key:
        return jsonify({"error": "user_id, companion_id, session_key are required"}), 400

    with session_scope() as db:
        if not db.get(User, user_id):
            return jsonify({"error": "user not found"}), 404
        if not db.get(Companion, companion_id):
            return jsonify({"error": "companion not found"}), 404
        conv = Conversation(user_id=user_id, companion_id=companion_id, session_key=session_key)
        db.add(conv)
        db.flush()
        return jsonify({"id": conv.id, "session_key": conv.session_key}), 201


@api.route("/conversations", methods=["GET"])
def list_conversations() -> Any:
    user_id = request.args.get("user_id", type=int)
    companion_id = request.args.get("companion_id", type=int)

    with session_scope() as db:
        stmt = select(Conversation)
        if user_id:
            stmt = stmt.where(Conversation.user_id == user_id)
        if companion_id:
            stmt = stmt.where(Conversation.companion_id == companion_id)
        convs = db.scalars(stmt).all()
        return jsonify([
            {
                "id": c.id,
                "user_id": c.user_id,
                "companion_id": c.companion_id,
                "session_key": c.session_key,
                "created_at": c.created_at.isoformat(),
            }
            for c in convs
        ])


# Chat endpoint
@api.route("/chat", methods=["POST"])
def chat() -> Any:
    payload = get_json()
    user_id = payload.get("user_id")
    companion_id = payload.get("companion_id")
    session_key = payload.get("session_key")
    user_input = (payload.get("input") or "").strip()

    if not user_id or not companion_id or not session_key or not user_input:
        return jsonify({"error": "user_id, companion_id, session_key, input are required"}), 400

    with session_scope() as db:
        user = db.get(User, user_id)
        companion = db.get(Companion, companion_id)
        if not user or not companion:
            return jsonify({"error": "user or companion not found"}), 404

        persona_vars = {
            "name": companion.name,
            "age": companion.age or "unknown",
            "gender": companion.gender or "unspecified",
            "birth_country": companion.birth_country or "unspecified",
            "personality": companion.personality or "friendly",
            "education": companion.education or "unspecified",
            "background": companion.background or "",
        }

        runnable = build_chain_with_memory(session_key, persona_vars)
        # Invoke the chain; RunnableWithMessageHistory takes config with configurable.thread_id but we set via with_config
        ai_msg = runnable.invoke({"input": user_input})
        # ai_msg is a BaseMessage or string; normalize to text
        content = getattr(ai_msg, "content", str(ai_msg))

        return jsonify({"response": content})


# History retrieval (from LangChain table)
@api.route("/history", methods=["GET"])
def history() -> Any:
    session_key = request.args.get("session_key")
    if not session_key:
        return jsonify({"error": "session_key is required"}), 400

    # Read via SQLChatMessageHistory for a consistent view
    from langchain_community.chat_message_histories import SQLChatMessageHistory
    from app.utils.config import settings

    hist = SQLChatMessageHistory(session_id=session_key, connection_string=settings.database_url)
    messages = [
        {"type": m.type, "content": getattr(m, "content", str(m))}
        for m in hist.messages
    ]
    return jsonify(messages)
