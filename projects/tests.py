from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Project, Skill

User = get_user_model()


class ProjectViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", name="Test", surname="User", password="pass123"
        )
        self.client.login(email="test@example.com", password="pass123")

    def test_project_list_view(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)

    def test_create_project_view(self):
        response = self.client.post(
            reverse("projects:create"),
            {"name": "New Project", "description": "Description", "status": "open"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), 1)

    def test_skill_filter(self):
        skill = Skill.objects.create(name="Python")
        project = Project.objects.create(name="Python Project", owner=self.user)
        project.skills.add(skill)

        response = self.client.get(reverse("projects:list") + "?skill=Python")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Project")
