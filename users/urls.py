from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("<int:user_id>/", views.user_detail_view, name="detail"),
    path("profile/edit/", views.edit_profile_submit, name="edit_profile"),
    path(
        "edit-profile/",
        RedirectView.as_view(url="/users/profile/edit/", permanent=False),
    ),
    path("change-password/", views.change_password_view, name="change_password"),
    path("list/", views.users_list_view, name="list"),
]
