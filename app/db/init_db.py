from app.domain.enums import Role
from app.services.mock_data_service import build_mock_chats


def init_db() -> None:
    from app.db.session import SessionLocal
    from app.models.mock_chat import MockChat
    from app.models.user import User

    db = SessionLocal()
    try:
        _ensure_user(db, "manager", "manager@example.com", "manager / 123456", Role.MANAGER.value)
        _ensure_user(db, "user", "user@example.com", "user / 123456", Role.NORMAL_USER.value)
        for chat in build_mock_chats():
            exists = db.query(MockChat).filter(MockChat.mock_chat_id == chat["mock_chat_id"]).first()
            if exists:
                continue
            db.add(
                MockChat(
                    mock_chat_id=chat["mock_chat_id"],
                    source_platform=chat["source_platform"],
                    business_line=chat["business_line"],
                    product_name=chat["product_name"],
                    scenario_type=chat["scenario_type"],
                    raw_content=chat["raw_content"],
                )
            )
        db.commit()
    finally:
        db.close()


def _ensure_user(db, username: str, email: str, password_hash: str, role: str) -> None:
    from app.models.user import User

    exists = db.query(User).filter(User.username == username).first()
    if exists:
        return
    db.add(User(username=username, email=email, password_hash=password_hash, role=role))


if __name__ == "__main__":
    init_db()
