from app.domain.enums import Role


def init_db() -> None:
    from app.db.session import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        _ensure_user(db, "manager", "manager@example.com", "manager / 123456", Role.MANAGER.value)
        _ensure_user(db, "user", "user@example.com", "user / 123456", Role.NORMAL_USER.value)
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
