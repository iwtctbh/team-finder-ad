from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from projects.models import Project, Skill

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            name="Test",
            surname="User",
            password="testpass123",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", name="Admin", surname="User", password="admin123"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class RegistrationTest(TestCase):
    def test_register_view(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "New",
                "surname": "User",
                "email": "new@example.com",
                "password": "testpass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 1)


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", name="Test", surname="User", password="pass123"
        )

    def test_create_project(self):
        project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            owner=self.user,
            status="open",
        )
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.owner, self.user)

    def test_project_str(self):
        project = Project.objects.create(name="Test Project", owner=self.user)
        self.assertEqual(str(project), "Test Project")


class SkillTest(TestCase):
    def test_create_skill(self):
        skill = Skill.objects.create(name="Python")
        self.assertEqual(str(skill), "Python")
