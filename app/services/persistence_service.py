from datetime import UTC, datetime


def build_persistence_values(task, result: dict) -> dict:
    segments = []
    knowledge_docs = []

    for segment in result.get("segments", []):
        segment_values = {
            "segment_no": segment["segment_no"],
            "process_task_id": task.id,
            "mock_chat_id": task.mock_chat_id,
            "original_content": segment.get("original_content"),
            "cleaned_content": segment.get("cleaned_content"),
            "desensitized_content": segment.get("desensitized_content"),
            "price_filtered_content": segment.get("price_filtered_content"),
            "customer_question": segment.get("customer_question"),
            "staff_answer": segment.get("staff_answer"),
            "business_line": segment.get("business_line"),
            "product_name": segment.get("product_name"),
            "tags": segment.get("tags"),
            "contains_sensitive_info": segment.get("contains_sensitive_info", False),
            "contains_price_info": segment.get("contains_price_info", False),
            "price_filter_status": segment.get("price_filter_status", "success"),
            "price_risk_level": segment.get("price_risk_level", "none"),
            "status": segment.get("status", "generated"),
        }
        segments.append(segment_values)

    for doc in result.get("knowledge_docs", []):
        knowledge_docs.append(
            {
                "segment_no": doc["doc_no"].removeprefix("kb_"),
                "doc_no": doc["doc_no"],
                "title": doc["title"],
                "content": doc["content"],
                "question_examples": doc.get("question_examples"),
                "tags": doc.get("tags"),
                "business_line": doc.get("business_line"),
                "product_name": doc.get("product_name"),
                "risk_level": doc.get("risk_level", "low"),
                "quality_score": doc.get("quality_score", 0),
                "review_status": doc.get("review_status", "pending_review"),
                "price_filtered": doc.get("price_filtered", False),
                "contains_price_intent": doc.get("contains_price_intent", False),
                "contains_original_price": doc.get("contains_original_price", False),
                "is_desensitized": doc.get("is_desensitized", True),
                "created_by": task.triggered_by,
                "updated_by": task.triggered_by,
            }
        )

    return {"segments": segments, "knowledge_docs": knowledge_docs}


def persist_pipeline_result(db, task, result: dict) -> dict:
    from app.models.dialogue_segment import DialogueSegment
    from app.models.knowledge_doc import KnowledgeDoc

    values = build_persistence_values(task, result)
    segment_by_no = {}

    for segment_values in values["segments"]:
        segment = DialogueSegment(**segment_values)
        db.add(segment)
        db.flush()
        segment_by_no[segment.segment_no] = segment

    for doc_values in values["knowledge_docs"]:
        segment_no = doc_values.pop("segment_no")
        segment = segment_by_no[segment_no]
        db.add(
            KnowledgeDoc(
                dialogue_segment_id=segment.id,
                **doc_values,
            )
        )

    task.status = "success"
    task.current_step = "completed"
    task.progress = 100
    task.step_result = result
    task.completed_at = datetime.now(UTC)
    db.commit()
    return values
