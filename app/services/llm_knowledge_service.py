from types import SimpleNamespace

from app.services.knowledge_service import generate_knowledge_doc
from app.services.llm_client_service import OpenAICompatibleLLMClient, is_llm_configured
from app.services.llm_prompt_service import build_knowledge_generation_messages
from app.services.llm_validation_service import extract_json_object, validate_llm_knowledge_doc


def generate_knowledge_doc_with_llm(
    segment: dict,
    db=None,
    related_type: str | None = None,
    related_id=None,
    client=None,
) -> dict:
    if client is None and not is_llm_configured():
        messages = build_knowledge_generation_messages(segment)
        _write_llm_log(
            db=db,
            related_type=related_type,
            related_id=related_id,
            client=SimpleNamespace(settings=None),
            prompt=_prompt_text(messages),
            request_payload={"messages": messages},
            response_payload=None,
            parsed_output=None,
            status="failed",
            error_message="LLM API key is not configured.",
            latency_ms=None,
        )
        return generate_knowledge_doc(segment)

    llm_client = client or OpenAICompatibleLLMClient()

    messages = build_knowledge_generation_messages(segment)
    result = None
    parsed_output = None

    try:
        result = llm_client.chat(
            messages,
            response_format={"type": "json_object"},
        )
        parsed_output = extract_json_object(result.content)
        doc = validate_llm_knowledge_doc(parsed_output, segment)
        _write_llm_log(
            db=db,
            related_type=related_type,
            related_id=related_id,
            client=llm_client,
            prompt=_prompt_text(messages),
            request_payload=result.request_payload,
            response_payload=result.response_payload,
            parsed_output=parsed_output,
            status="success",
            error_message=None,
            latency_ms=result.latency_ms,
        )
        return doc
    except Exception as exc:
        _write_llm_log(
            db=db,
            related_type=related_type,
            related_id=related_id,
            client=llm_client,
            prompt=_prompt_text(messages),
            request_payload=getattr(result, "request_payload", {"messages": messages}),
            response_payload=getattr(result, "response_payload", None),
            parsed_output=parsed_output,
            status="failed",
            error_message=str(exc),
            latency_ms=getattr(result, "latency_ms", None),
        )
        return generate_knowledge_doc(segment)


def _write_llm_log(
    db,
    related_type,
    related_id,
    client,
    prompt,
    request_payload,
    response_payload,
    parsed_output,
    status,
    error_message,
    latency_ms,
) -> None:
    if db is None:
        return

    settings = getattr(client, "settings", None)
    record = _create_llm_call_log(
        related_type=related_type,
        related_id=related_id,
        provider="openai_compatible",
        model_name=getattr(settings, "llm_model_name", None),
        prompt=prompt,
        request_payload=request_payload,
        response_payload=response_payload,
        parsed_output=parsed_output,
        status=status,
        error_message=error_message,
        latency_ms=latency_ms,
    )
    db.add(record)
    if hasattr(db, "flush"):
        db.flush()


def _create_llm_call_log(**values):
    try:
        from app.models.llm_call_log import LLMCallLog
    except ModuleNotFoundError:
        return SimpleNamespace(**values)
    return LLMCallLog(**values)


def _prompt_text(messages: list[dict]) -> str:
    return "\n\n".join(f"{message.get('role')}: {message.get('content')}" for message in messages)
