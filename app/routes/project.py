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
        "project/project_browser.html",
        owned_projects=current_user.owned_projects,
        projects=current_user.projects,
    )


@bp.route("/project/<id>")
@login_required
def project(id: str) -> str:
    project = Project.query.get(id)
    participants = None

    if project is not None:
        # Check if it's a project that user has access to
        is_owner = current_user.id == project.owner_id
        is_participant = current_user in project.participants

        if not is_owner and not is_participant:
            project = None
        else:
            participants = project.participants

    return render_template(
        "project/project.html",
        project=project,
        participants=participants,
    )
