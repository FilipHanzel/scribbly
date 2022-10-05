from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models import Project

bp = Blueprint(
    name="project",
    import_name=__name__,
)


@bp.route("/projects")
@login_required
def projects() -> str:
    return render_template(
        "project/project_browser.html", owned_projects=current_user.owned_projects
    )


@bp.route("/project/<id>")
@login_required
def project(id: str) -> str:
    project = Project.query.get(id)

    # Check if it's a project that user doesn't have access to
    if project is not None and project.owner_id != current_user.id:
        project = None

    return render_template("project/project.html", project=project)
