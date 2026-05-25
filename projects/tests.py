from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Project, Skill

User = get_user_model()

TEST_EMAIL = "test@example.com"
TEST_NAME = "Test"
TEST_SURNAME = "User"
TEST_PASSWORD = "pass123"
TEST_PROJECT_NAME = "New Project"
TEST_PROJECT_DESCRIPTION = "Description"
TEST_PROJECT_STATUS = "open"
TEST_SKILL_NAME = "Python"
TEST_PYTHON_PROJECT_NAME = "Python Project"


class ProjectViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL,
            name=TEST_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD,
        )
        self.client.login(email=TEST_EMAIL, password=TEST_PASSWORD)

    def test_project_list_view(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)  # 200

    def test_create_project_view(self):
        response = self.client.post(
            reverse("projects:create"),
            {
                "name": TEST_PROJECT_NAME,
                "description": TEST_PROJECT_DESCRIPTION,
                "status": TEST_PROJECT_STATUS,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # 302
        self.assertEqual(Project.objects.count(), 1)

    def test_skill_filter(self):
        skill = Skill.objects.create(name=TEST_SKILL_NAME)
        project = Project.objects.create(name=TEST_PYTHON_PROJECT_NAME, owner=self.user)
        project.skills.add(skill)

        response = self.client.get(
            reverse("projects:list") + f"?skill={TEST_SKILL_NAME}"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)  # 200
        self.assertContains(response, TEST_PYTHON_PROJECT_NAME)
