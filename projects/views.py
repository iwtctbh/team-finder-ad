from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Project
from .forms import ProjectForm


def project_list_view(request):
    projects_list = Project.objects.filter(status="open").order_by("-created_at")
    paginator = Paginator(projects_list, 12)
    page_number = request.GET.get("page")
    projects = paginator.get_page(page_number)

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
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return JsonResponse({"error": "Нет прав"}, status=403)

    if project.status == "open":
        project.status = "closed"
        project.save()

    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.status != "open":
        return JsonResponse({"error": "Проект закрыт"}, status=400)

    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_participating = False
    else:
        project.participants.add(request.user)
        is_participating = True

    return JsonResponse({"status": "ok", "is_participating": is_participating})
