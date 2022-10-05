from flask import Blueprint, render_template
from flask_login import current_user, login_required

bp = Blueprint(
    name="project",
    import_name=__name__,
)


@bp.route("/projects")
@login_required
def projects() -> str:
    return render_template(
        "project/projects.html", owned_projects=current_user.owned_projects
    )
