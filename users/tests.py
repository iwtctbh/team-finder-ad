from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from projects.models import Project, Skill

User = get_user_model()

TEST_EMAIL = "test@example.com"
TEST_ADMIN_EMAIL = "admin@example.com"
TEST_NEW_EMAIL = "new@example.com"
TEST_NAME = "Test"
TEST_SURNAME = "User"
TEST_ADMIN_NAME = "Admin"
TEST_NEW_NAME = "New"
TEST_PASSWORD = "testpass123"
TEST_ADMIN_PASSWORD = "admin123"
TEST_PROJECT_NAME = "Test Project"
TEST_PROJECT_DESCRIPTION = "Test Description"
TEST_SKILL_NAME = "Python"


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email=TEST_EMAIL,
            name=TEST_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD,
        )
        self.assertEqual(user.email, TEST_EMAIL)
        self.assertTrue(user.check_password(TEST_PASSWORD))

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email=TEST_ADMIN_EMAIL,
            name=TEST_ADMIN_NAME,
            surname=TEST_SURNAME,
            password=TEST_ADMIN_PASSWORD,
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class RegistrationTest(TestCase):
    def test_register_view(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": TEST_NEW_NAME,
                "surname": TEST_SURNAME,
                "email": TEST_NEW_EMAIL,
                "password": TEST_PASSWORD,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(User.objects.count(), 1)


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL,
            name=TEST_NAME,
            surname=TEST_SURNAME,
            password=TEST_PASSWORD,
        )

    def test_create_project(self):
        project = Project.objects.create(
            name=TEST_PROJECT_NAME,
            description=TEST_PROJECT_DESCRIPTION,
            owner=self.user,
            status="open",
        )
        self.assertEqual(project.name, TEST_PROJECT_NAME)
        self.assertEqual(project.owner, self.user)

    def test_project_str(self):
        project = Project.objects.create(name=TEST_PROJECT_NAME, owner=self.user)
        self.assertEqual(str(project), TEST_PROJECT_NAME)


class SkillTest(TestCase):
    def test_create_skill(self):
        skill = Skill.objects.create(name=TEST_SKILL_NAME)
        self.assertEqual(str(skill), TEST_SKILL_NAME)
