from http import HTTPStatus
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User
from .forms import (
    RegistrationForm,
    LoginForm,
    ProfileEditForm,
    CustomPasswordChangeForm,
)
from .pagination import paginate_queryset


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
    else:
        form = RegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("projects:list")
        else:
            form.add_error(None, "Неверный имейл или пароль")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id, is_active=True)
    projects = user_obj.owned_projects.all()
    is_owner = request.user == user_obj

    return render(
        request,
        "users/user-details.html",
        {
            "user": user_obj,
            "projects": projects,
            "is_owner": is_owner,
        },
    )


@login_required
def edit_profile_submit(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен")
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = ProfileEditForm(instance=request.user)

    return render(
        request, "users/edit_profile.html", {"form": form, "user": request.user}
    )


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно изменен")
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, "users/change_password.html", {"form": form})


def users_list_view(request):
    users_list = User.objects.filter(is_active=True).order_by("-date_joined")
    participants = paginate_queryset(request, users_list)

    return render(
        request,
        "users/participants.html",
        {"participants": participants},
    )
