from flask import Blueprint, render_template
from flask_login import current_user

bp = Blueprint(
    name="project",
    import_name=__name__,
)


@bp.route("/projects")
def projects() -> str:
    return render_template("project/projects.html")
