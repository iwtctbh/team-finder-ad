import random
from io import BytesIO

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    NAME_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    ABOUT_MAX_LENGTH,
    AVATAR_SIZE,
    AVATAR_FONT_SIZE,
    AVATAR_COLORS,
)
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name="Имя")
    surname = models.CharField(max_length=SURNAME_MAX_LENGTH, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/default.png", verbose_name="Аватар"
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        validators=[
            RegexValidator(
                regex=r"^(\+7|8)\d{10}$",
                message="Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX",
            )
        ],
        unique=False,
        blank=True,
        null=True,
        verbose_name="Телефон",
    )
    github_url = models.URLField(blank=True, null=True, verbose_name="GitHub")
    about = models.TextField(
        max_length=ABOUT_MAX_LENGTH, blank=True, null=True, verbose_name="О себе"
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

    def _generate_avatar(self):
        size = AVATAR_SIZE
        color = random.choice(AVATAR_COLORS)

        image = Image.new("RGB", size, color)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
        except OSError:
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

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = self._generate_avatar()
        super().save(*args, **kwargs)
