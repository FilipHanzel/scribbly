"""
ORM models.

Models implement only the most basic functionality.
More complex queries are implemented in the methods
responsible for given functionality.
"""


from __future__ import annotations

from base64 import urlsafe_b64encode
from typing import Optional
from uuid import uuid4

from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

association_user_project = db.Table(
    "user_project",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("project_id", db.String(), db.ForeignKey("project.id")),
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


def generate_key() -> str:
    """Generate random url safe string."""
    return urlsafe_b64encode(uuid4().bytes).decode("utf-8").rstrip("=")


class Project(db.Model):  # type: ignore
    __tablename__ = "project"

    id = db.Column(db.String(22), primary_key=True, default=generate_key)
    name = db.Column(db.String(255), unique=False, nullable=False)
    description = db.Column(db.String(2048), nullable=True)
    created_at = db.Column(db.DateTime(), server_default=func.now())

    # Relations with User
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", back_populates="owned_projects")

    participants = db.relationship(
        "User", secondary=association_user_project, back_populates="projects"
    )

    @classmethod
    def add(
        cls, name: str, description: Optional[str], owner: User
    ) -> Optional[Project]:
        """
        Add new project and map it to existing user.

        This method can theoretically fail, since Project class uses UUID4 as primary_key.
        """
        project = cls(name=name, description=description, owner_id=owner.id)
        # Make sure owner is also a participant in the project
        project.participants.append(owner)

        db.session.add(project)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            # Second attempt to generate key
            project.id = generate_key()
            db.session.add(project)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return None

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

            project_a = Project.add("niceOne", "A description.", user_a)

            if project_a is None:
                raise Exception("Failed to create project_a")

            Project.add("myProject", None, user_a)
            Project.add("princess", "No need for description.", user_c)
            Project.add("someProject", "Some description.", user_a)
            Project.add("someOtherProject", "Description.", user_a)
            Project.add("anotherProject", "Another description.", user_a)
            Project.add("yetAnotherProject", None, user_a)
            project_h = Project.add("andAnotherOne", None, user_b)

            if project_h is None:
                raise Exception("Failed to create project_h")

            project_a.participants.append(user_b)
            project_a.participants.append(user_c)
            project_h.participants.append(user_a)

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
