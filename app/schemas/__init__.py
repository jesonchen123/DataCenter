try:
    from pydantic import BaseModel, Field
except ModuleNotFoundError:  # pragma: no cover
    BaseModel = object

    def Field(default=None, **_kwargs):
        return default


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class MockChatResponse(BaseModel):
    id: str | None = None
    mock_chat_id: str
    source_platform: str
    business_line: str | None = None
    product_name: str | None = None
    scenario_type: str | None = None
    raw_content: dict = Field(default_factory=dict)


class ManualMockChatMessageRequest(BaseModel):
    message_id: str | None = None
    sender_role: str | None = None
    role: str | None = None
    sender_name: str | None = None
    sender: str | None = None
    message_time: str | None = None
    content: str | None = None
    text: str | None = None


class ManualMockChatCreateRequest(BaseModel):
    mock_chat_id: str
    source_platform: str = "manual_test"
    business_line: str | None = None
    product_name: str | None = None
    scenario_type: str | None = None
    messages: list[ManualMockChatMessageRequest] = Field(default_factory=list)


class ProcessTaskResponse(BaseModel):
    id: str
    task_no: str
    status: str
    current_step: str | None = None
    progress: int = 0
    error_message: str | None = None
    step_result: dict | None = None


class KnowledgeDocUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    question_examples: list[str] | None = None
    tags: list[str] | None = None


class ReviewRequest(BaseModel):
    approved: bool
    review_comment: str | None = None


class ExportRequest(BaseModel):
    knowledge_doc_ids: list[str] = Field(default_factory=list)


class ExportTaskResponse(BaseModel):
    id: str
    export_no: str
    status: str
    document_count: int = 0
    export_content: dict | None = None
