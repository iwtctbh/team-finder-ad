from http import HTTPStatus

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Project
from .forms import ProjectForm
from .pagination import paginate_queryset
from .constants import PROJECT_STATUS_OPEN, PROJECT_STATUS_CLOSED


def project_list_view(request):
    projects_list = Project.objects.filter(status=PROJECT_STATUS_OPEN).order_by(
        "-created_at"
    )
    projects = paginate_queryset(request, projects_list)

    return render(request, "projects/project_list.html", {"projects": projects})


def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    is_owner = request.user == project.owner
    is_participant = request.user in project.participants.all()

    return render(
        request,
        "projects/project-details.html",
        {
            "project": project,
            "is_owner": is_owner,
            "is_participant": is_participant,
        },
    )


@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm()

    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        messages.error(request, "Вы не можете редактировать этот проект")
        return redirect("projects:detail", project_id=project.id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": True}
    )


@login_required
def complete_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Проект не найден"}, status=HTTPStatus.NOT_FOUND)

    if project.owner != request.user:
        return JsonResponse({"error": "Нет прав"}, status=HTTPStatus.FORBIDDEN)

    if project.status == PROJECT_STATUS_OPEN:
        project.status = PROJECT_STATUS_CLOSED
        project.save()

    return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})


@login_required
def toggle_participate(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Проект не найден"}, status=HTTPStatus.NOT_FOUND)

    if project.status != PROJECT_STATUS_OPEN:
        return JsonResponse({"error": "Проект закрыт"}, status=HTTPStatus.BAD_REQUEST)

    is_participating = project.participants.filter(id=request.user.id).exists()

    if is_participating:
        project.participants.remove(request.user)
        is_participating = False
    else:
        project.participants.add(request.user)
        is_participating = True

    return JsonResponse({"status": "ok", "is_participating": is_participating})
