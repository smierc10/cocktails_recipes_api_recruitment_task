from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

handle_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9_]+$",
    message="handle nie może zaweirać innych znaków niż litery alfabetu lub znak podkreślenia",
)


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    handle = models.CharField(
        max_length=32,
        unique=True,
        blank=False,
        validators=[handle_validator],
        help_text="Maksymalnie 32 znaki, składa się tylko z małych liter oraz znaku podkreślenia",
    )
