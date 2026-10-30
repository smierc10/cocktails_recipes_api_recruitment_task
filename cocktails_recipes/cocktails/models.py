from decimal import Decimal
import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError

# Create your models here.


class CocktailCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name.__str__()

    class Meta:
        verbose_name_plural = "Cocktail categories"


class CocktailRecipe(models.Model):
    name = models.CharField(max_length=50)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cocktails_set"
    )
    category = models.ForeignKey(CocktailCategory, on_delete=models.PROTECT)
    instructions = models.TextField()
    banner_image_url = models.URLField(verbose_name="Cocktail banner image", blank=True)

    def __str__(self):
        return self.name.__str__()


class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image_url = models.URLField()
    is_alcoholic = models.BooleanField()
    is_vegan = models.BooleanField()
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.name.__str__()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(CocktailRecipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.FloatField()
    unit = models.CharField(max_length=20)

    def __str__(self):
        return (
            self.ingredient.__str__()
            + " "
            + self.amount.__str__()
            + " "
            + self.unit.__str__()
        )


def step_of_0_1_validator(value):
    if (value * 10) % 1 != 0:
        raise ValidationError("Rating must be in increments of 0.1")


class Review(models.Model):
    recipe = models.ForeignKey(CocktailRecipe, on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=100, blank=True)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("1.0")),
            MaxValueValidator(Decimal("5.0")),
            step_of_0_1_validator,
        ],
    )
    text = models.TextField(blank=True)


def get_image_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"images/{instance.id}.{ext}"


class UploadedImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to=get_image_upload_path)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def delete(self, using=None, keep_parents=False):
        img = self.image
        if img:
            img.delete(save=False)
        return super().delete(using, keep_parents)
