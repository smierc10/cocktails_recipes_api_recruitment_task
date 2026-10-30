from django.contrib import admin
from .models import (
    CocktailCategory,
    CocktailRecipe,
    Ingredient,
    RecipeIngredient,
    Review,
    UploadedImage,
)
from django.utils.html import format_html


# Register your models here
class IngredientInLine(admin.TabularInline):
    model = Ingredient


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(CocktailRecipe)
class CocktailRecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInLine]
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.banner_image_url:
            return format_html(
                '<img src="{}" style="max-height: 400px; max-width: 1000px;/>',
                obj.banner_image_url,
            )
        return "-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height: 400px; max-width: 1000px;/>',
                obj.image_url,
            )
        return "-"


@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        return format_html(
            '<img src="{}" style="max-height: 400px; max-width: 1000px; display: block;"/>',
            obj.image.url,
        )
        return "-"


admin.site.register(CocktailCategory)
admin.site.register(Review)
