from django.contrib import admin

from .models import Project, Skill


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = (
        "name",
        "description",
        "owner__email",
        "owner__name",
        "owner__surname",
    )
    filter_horizontal = ("participants", "skills")
    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("name", "description", "owner", "status", "github_url")},
        ),
        ("Участники и навыки", {"fields": ("participants", "skills")}),
        ("Даты", {"fields": ("created_at",)}),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
