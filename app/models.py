from __future__ import annotations

from typing import Optional

from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):  # type: ignore
    __tablename__ = "user"

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=func.now())

    @classmethod
    def add(cls, email: str, username: str, password: str) -> None:
        user = cls(
            email=email,
            username=username,
            password=generate_password_hash(password, method="sha256"),
        )
        db.session.add(user)
        db.session.commit()

    @classmethod
    def get(cls, email: str) -> Optional[User]:
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_id(cls, id: str) -> Optional[User]:
        return cls.query.get(id)

    @classmethod
    def is_username_available(cls, username: str) -> bool:
        return cls.query.filter_by(username=username).first() is None

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)


def register_db_utils(app: Flask) -> None:
    """Database testing utilities."""

    @app.cli.command("db-fake")
    def db_fake_data() -> None:
        """Commit dummy data to the database."""
        with app.app_context():
            User.add(
                email="email@email.com",
                username="username",
                password="123456789",
            )

    @app.cli.command("db-drop")
    def db_drop_data() -> None:
        """Crop and recreate the database."""
        with app.app_context():
            db.drop_all()
            db.create_all()
