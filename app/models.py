"""
ORM models.

Models implement only the most basic functionality.
More complex queries are implemented in the methods
responsible for given functionality.
"""


from __future__ import annotations

from typing import Optional

from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

association_user_project = db.Table(
    "user_project",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("project_id", db.Integer(), db.ForeignKey("project.id")),
)


class User(db.Model, UserMixin):  # type: ignore
    __tablename__ = "user"

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=func.now())

    # Relations with Project
    owned_projects = db.relationship("Project", back_populates="owner")

    projects = db.relationship(
        "Project", secondary=association_user_project, back_populates="participants"
    )

    @classmethod
    def add(cls, email: str, username: str, password: str) -> User:
        user = cls(
            email=email,
            username=username,
            password=generate_password_hash(password, method="sha256"),
        )
        db.session.add(user)
        db.session.commit()

        return user

    @classmethod
    def get_by_email(cls, email: str) -> Optional[User]:
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_id(cls, id: str) -> Optional[User]:
        return cls.query.get(id)

    @classmethod
    def is_email_available(cls, email: str) -> bool:
        return cls.get_by_email(email) is None

    @classmethod
    def is_username_available(cls, username: str) -> bool:
        return cls.query.filter_by(username=username).first() is None

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def update(
        self,
        email: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        if email is not None:
            self.email = email
        if username is not None:
            self.username = username
        if password is not None:
            self.password = generate_password_hash(password, method="sha256")

        if any([email, username, password]):
            db.session.commit()


class Project(db.Model):  # type: ignore
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(), server_default=func.now())

    # Relations with User
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", back_populates="owned_projects")

    participants = db.relationship(
        "User", secondary=association_user_project, back_populates="projects"
    )

    @classmethod
    def add(cls, name: str, description: Optional[str], owner: User) -> Project:
        project = cls(name=name, description=description, owner_id=owner.id)
        # Make sure owner is also a participant in the project
        project.participants.append(owner)

        db.session.add(project)
        db.session.commit()

        return project


def register_db_utils(app: Flask) -> None:
    """Database testing utilities."""

    @app.cli.command("db-fake")
    def db_fake_data() -> None:
        """Commit dummy data to the database."""
        with app.app_context():
            user_a = User.add("email@email.com", "username", "123456789")
            user_b = User.add("email@example.com", "someone", "abcd1234")
            user_c = User.add("someone@somewhere.com", "luigi", "betterthanmario")

            db.session.add(user_a)
            db.session.add(user_b)
            db.session.add(user_c)

            project_a = Project.add("niceOne", "A description.", user_a)
            project_b = Project.add("myProject", None, user_a)
            project_c = Project.add("princess", "No need for description.", user_c)

            project_a.participants.append(user_b)
            project_a.participants.append(user_c)

            db.session.add(project_a)
            db.session.add(project_b)
            db.session.add(project_c)

            db.session.commit()

    @app.cli.command("db-drop")
    def db_drop_data() -> None:
        """Crop and recreate the database."""
        with app.app_context():
            db.drop_all()
            db.create_all()

    @app.cli.command("db-test")
    def db_test() -> None:
        """Temporary method to test ORM during development."""
