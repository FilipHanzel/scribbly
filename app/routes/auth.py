from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from flask import (
    Blueprint,
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
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
        "Email",
        validators=EMAIL_VALIDATORS,
        name="email-address",
    )
    password = PasswordField(
        "Password",
        validators=PASSWORD_VALIDATORS,
        name="password",
    )
    remember_me = BooleanField("Remember me", name="remember me")

    def validate(self) -> bool:
        """In addition to standard validation, check if user exists."""
        if not super().validate():
            return False

        user = User.get_by_email(self.email.data)
        if not user or not user.check_password(self.password.data):
            msg = "Incorrect email or password."
            self.email.errors.append(msg)
            self.password.errors.append(msg)
            return False

        return True


class RegisterForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=EMAIL_VALIDATORS,
        name="email-address",
    )
    username = StringField(
        "Username",
        validators=USERNAME_VALIDATORS,
        name="username",
    )
    password = PasswordField(
        "Password",
        validators=PASSWORD_VALIDATORS,
        name="password",
    )
    confirm = PasswordField(
        "Confirm password",
        validators=CONFIRM_VALIDATORS,
        name="confirmation",
    )

    def validate(self) -> bool:
        """In addition to standard validation, check if email and/or username are taken."""
        if not super().validate():
            return False

        if not User.is_email_available(self.email.data):
            self.email.errors.append("Email address already taken.")
            return False

        if not User.is_username_available(self.username.data):
            self.username.errors.append("Username already taken.")
            return False

        return True


class ProfileForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=EMAIL_VALIDATORS,
        name="email-address",
    )
    username = StringField(
        "Username",
        validators=USERNAME_VALIDATORS,
        name="username",
    )

    def validate(self) -> bool:
        """In addition to standard validation, check if email and/or username are taken."""
        print("VALIDATING!")
        if not super().validate():
            return False

        if not current_user.is_authenticated:
            return False

        # Look for different user with the same username or email
        user = User.query.filter(
            User.id != current_user.id,
            sa.or_(
                User.username == self.username.data,
                User.email == self.email.data,
            ),
        ).first()

        if user is not None:
            if user.email == current_user.email:
                self.email.errors.append("Email address already taken.")
            if user.username == current_user.username:
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
        session["login_message"] = ["You cannot go there!", "Please log in."]
        return redirect(url_for("auth.login"))


bp = Blueprint(
    name="auth",
    import_name=__name__,
    url_prefix="/auth",
)


@bp.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    form = LoginForm()
    if form.validate_on_submit():

        user = User.get_by_email(form.email.data)
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("home.home"))

    return render_template("auth/login.html", login_form=form)


@bp.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for("home.home"))


@bp.route("/register", methods=["GET", "POST"])
def register() -> Response | str:
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        User.add(
            email=form.email.data.strip(),
            username=form.username.data,
            password=form.password.data,
        )

        session["login_message"] = ["Registration successful!", "Please log in."]
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", register_form=form)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile() -> str:

    form = ProfileForm()

    if form.validate_on_submit():
        current_user.update(
            email=form.email.data,
            username=form.username.data,
        )

    form.email.data = current_user.email
    form.username.data = current_user.username
    return render_template("auth/profile.html", profile_form=form)
