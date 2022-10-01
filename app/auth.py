from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from flask import Blueprint, Flask, g, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.models import User

if TYPE_CHECKING:
    from werkzeug.wrappers import Response

EMAIL_VALIDATORS = [
    DataRequired(message="Email address is required."),
    Email(message="Please enter valid email address."),
    Length(max=255, message="Email address too long."),
]

USERNAME_VALIDATORS = [
    DataRequired(message="Username is required."),
    Length(min=4, message="Username must be at least 4 characters long."),
    Length(max=255, message="Username cannot be longer than 255 characters."),
]

PASSWORD_VALIDATORS = [
    DataRequired(message="Password is required."),
    Length(min=8, message="Password must be at least 8 characters long."),
]

CONFIRM_VALIDATORS = [
    DataRequired(message="Confirmation is required."),
    Length(min=8, message="Confirmation must be at least 8 characters long."),
    EqualTo("password", message="Passwords must match."),
]


class LoginForm(FlaskForm):
    email = EmailField(
        "email",
        validators=EMAIL_VALIDATORS,
        name="email address",
    )
    password = PasswordField(
        "password",
        validators=PASSWORD_VALIDATORS,
        name="password",
    )
    remember_me = BooleanField(
        "remember_me",
        name="remember me",
    )

    def validate(self) -> bool:
        """In addition to standard validation, check if user exists."""
        if not super().validate():
            return False

        user = User.get(self.email.data)
        if not user or not user.check_password(self.password.data):
            msg = "Incorrect email or password."
            self.email.errors.append(msg)
            self.password.errors.append(msg)
            return False

        return True


class RegisterForm(FlaskForm):
    email = EmailField(
        "email",
        validators=EMAIL_VALIDATORS,
        name="email address",
    )
    username = StringField(
        "username",
        validators=USERNAME_VALIDATORS,
        name="username",
    )
    password = PasswordField(
        "password",
        validators=PASSWORD_VALIDATORS,
        name="password",
    )
    confirm = PasswordField(
        "confirm password",
        validators=CONFIRM_VALIDATORS,
        name="confirmation",
    )

    def validate(self) -> bool:
        """In addition to standard validation, check if email and/or username are taken."""
        if not super().validate():
            return False

        if User.get(self.email.data):
            self.email.errors.append("Email address already taken.")
            return False

        if not User.is_username_available(self.username.data):
            self.username.errors.append("Username already taken.")
            return False

        return True


def register_login_manager(login_manager: LoginManager) -> None:
    """Register Flask-Login handlers."""

    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[User]:
        """Verify if user is logged in. Runs after every page load."""
        if user_id is not None:
            return User.query.get(user_id)
        return None

    @login_manager.unauthorized_handler
    def unauthorized() -> Response:
        """Redirect to login page on every unauthorized request."""
        return redirect(url_for("auth.login"))


bp = Blueprint(
    name="auth",
    import_name=__name__,
    url_prefix="/auth",
    template_folder="templates/auth",
)


@bp.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():

        user = User.get(form.email.data)
        login_user(user, remember=form.remember_me.data)

        return redirect(url_for("home"))

    return render_template("auth/login.html", login_form=form)


@bp.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for("home"))


@bp.route("/register", methods=["GET", "POST"])
def register() -> Response | str:
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegisterForm()
    if form.validate_on_submit():
        User.add(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", register_form=form)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile() -> str:
    return render_template("auth/profile.html")
