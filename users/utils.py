from django.core.exceptions import ValidationError

from .constants import PHONE_MAX_LENGTH
from .models import User


def normalize_phone(phone):
    if phone and phone.startswith("8"):
        return "+7" + phone[1:]
    return phone


def validate_unique_phone(phone, user_id=None):
    if not phone:
        return phone

    phone = normalize_phone(phone)

    query = User.objects.filter(phone=phone)
    if user_id:
        query = query.exclude(pk=user_id)

    if query.exists():
        raise ValidationError("Пользователь с таким номером телефона уже существует")

    return phone


def validate_github_url(url):
    if url and "github.com" not in url:
        raise ValidationError("Ссылка должна вести на GitHub")
    return url
