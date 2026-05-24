from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.validators import RegexValidator
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    AVATAR_COLORS = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#96CEB4",
        "#FFEAA7",
        "#DDA0DD",
        "#98D8C8",
        "#F7DC6F",
        "#BB8FCE",
        "#85C1E2",
    ]

    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=124, verbose_name="Имя")
    surname = models.CharField(max_length=124, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/default.png", verbose_name="Аватар"
    )
    phone = models.CharField(
        max_length=12,
        validators=[
            RegexValidator(
                regex=r"^(\+7|8)\d{10}$",
                message="Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX",
            )
        ],
        unique=False,  # Убираем unique=True
        blank=True,
        null=True,
        verbose_name="Телефон",
    )
    github_url = models.URLField(blank=True, null=True, verbose_name="GitHub")
    about = models.TextField(
        max_length=256, blank=True, null=True, verbose_name="О себе"
    )

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}"

    def get_full_name(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        size = (200, 200)
        color = random.choice(self.AVATAR_COLORS)

        image = Image.new("RGB", size, color)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except:
            font = ImageFont.load_default()

        letter = self.name[0].upper() if self.name else "?"

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)

        draw.text(position, letter, fill="white", font=font)

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        return ContentFile(buffer.getvalue(), name=f"avatar_{self.email}.png")
