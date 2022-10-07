from __future__ import annotations

from flask import Blueprint, Response, make_response, render_template, request
from flask_login import current_user, login_required

from app.models import Project

bp = Blueprint(
    name="project",
    import_name=__name__,
)


RECENT_PROJECTS_QUEUE_SIZE = 5


def get_recent_projects_cookie_name() -> str:
    """
    Generate recent projects cookie name for current_user.

    Requires request context to get current_user.
    """
    return f"recent-{current_user.username}"


def get_recent_projects_ids(cookie_name: str) -> list[str]:
    """
    Get and parse a cookie with a list of projects recently visited by current_user.

    Requires request context to get a cookie.
    """
    cookie = request.cookies.get(cookie_name)
    cookie_parsed = cookie.split(",")[:RECENT_PROJECTS_QUEUE_SIZE] if cookie else []

    return cookie_parsed


def get_recent_projects(recent_projects_ids: list[str]) -> list[Project]:
    """
    Get all the recent projects current_user has access to.

    Requires request context to get current_user.
    """
    return [
        project
        for recent_id in recent_projects_ids
        for project in current_user.projects
        if str(project.id) == recent_id
    ]


def rotate_recent_projects_ids(
    recent_projects: list[str], project_id: str
) -> list[str]:
    """
    Add project_id to the list of projects recently visited by current_user.

    If project_id is already in the list, move it up the list.
    """
    if project_id not in recent_projects:
        if len(recent_projects) >= RECENT_PROJECTS_QUEUE_SIZE:
            del recent_projects[-1]
    else:
        recent_projects.remove(project_id)

    recent_projects.insert(0, project_id)

    return recent_projects


@bp.route("/projects")
@login_required
def projects_browser() -> str:

    # Get recent projects (make sure current_user has access to them)
    cookie_name = get_recent_projects_cookie_name()
    recent_ids = get_recent_projects_ids(cookie_name)
    recent_projects = get_recent_projects(recent_ids)

    return render_template(
        "project/project_browser.html",
        recent_projects=recent_projects,
        owned_projects=current_user.owned_projects,
        projects=current_user.projects,
    )


@bp.route("/project/<project_id>")
@login_required
def project(project_id: str) -> Response | str:
    project = Project.query.get(project_id)

    # Check if it's a project that user has access to
    if project is not None and current_user in project.participants:
        response = make_response(
            render_template(
                "project/project.html",
                project=project,
                participants=project.participants,
            )
        )

        # Rotate recently visited projects
        cookie_name = get_recent_projects_cookie_name()
        recent = get_recent_projects_ids(cookie_name)
        recent = rotate_recent_projects_ids(recent, project_id)

        response.set_cookie(
            cookie_name,
            ",".join(recent),
            httponly=True,
            samesite="Lax",
        )

        return response

    return render_template("project/project.html")
