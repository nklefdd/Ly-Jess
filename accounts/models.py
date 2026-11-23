from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+380\d{9}$",
    message="Телефон має бути у форматі +380XXXXXXXXX.",
)


class User(AbstractUser):
    """Користувач магазину. Адміністратор — користувач з is_staff=True."""

    email = models.EmailField("email", unique=True)
    phone = models.CharField("телефон", max_length=13, blank=True, validators=[phone_validator])

    class Meta:
        ordering = ["id"]
        verbose_name = "користувач"
        verbose_name_plural = "користувачі"

    @property
    def role(self):
        return "admin" if self.is_staff else "user"
