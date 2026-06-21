from enum import StrEnum


class Role(StrEnum):
    MANAGER = "manager"
    NORMAL_USER = "normal_user"


class ReviewStatus(StrEnum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEED_EDIT = "need_edit"
    ARCHIVED = "archived"


class RiskLevel(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PriceFilterStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
