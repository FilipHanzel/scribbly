from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

if TYPE_CHECKING:
    from werkzeug.wrappers import Response

bp = Blueprint(
    name="home",
    import_name=__name__,
)


@bp.route("/")
def home() -> Response | str:
    if current_user.is_authenticated:
        return redirect(url_for("project.projects"))

    return render_template("home.html")
