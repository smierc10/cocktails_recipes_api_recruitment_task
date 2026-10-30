from .models import (
    CocktailCategory,
    CocktailRecipe,
    Ingredient,
    RecipeIngredient,
    Review,
    UploadedImage,
)
from rest_framework import serializers


class ReviewWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["title", "rating", "text"]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.handle")

    class Meta:
        model = Review
        fields = ["title", "rating", "text", "author", "id"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CocktailCategory
        fields = ["name"]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["name", "description", "is_alcoholic", "is_vegan", "image_url"]


# Recipe Ingredient serializers


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        source="ingredient", slug_field="id", queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount", "unit"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.SlugRelatedField(slug_field="name", read_only=True)
    image_url = serializers.SlugRelatedField(
        source="ingredient", slug_field="image_url", read_only=True
    )

    url = serializers.HyperlinkedRelatedField(
        source="ingredient", view_name="ingredient-detail", read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "amount", "unit", "image_url", "url"]


# Cocktail Recipe Serializers


class CocktailRecipeListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = CocktailRecipe
        fields = ["name", "category", "rating"]


class CocktailRecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(
        source="recipeingredient_set", many=True
    )
    category = serializers.SlugRelatedField(
        slug_field="name", queryset=CocktailCategory.objects.all()
    )

    class Meta:
        model = CocktailRecipe
        fields = ["name", "category", "banner_image_url", "ingredients", "instructions"]

    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipeingredient_set")
        cocktail = CocktailRecipe.objects.create(**validated_data)

        for data in ingredients_data:
            RecipeIngredient.objects.create(recipe=cocktail, **data)

        return cocktail

    def update(self, instance, validated_data):
        print(validated_data)
        ingredients_data = validated_data.get("recipeingredient_set", None)

        instance.name = validated_data.get("name", instance.name)
        instance.category = validated_data.get("categoru", instance.category)
        instance.instructions = validated_data.get(
            "instructions", instance.instructions
        )
        instance.save()

        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()

            for data in ingredients_data:
                RecipeIngredient.objects.create(recipe=instance, **data)

        return instance


class CocktailRecipeDetailSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source="recipeingredient_set", many=True, read_only=True
    )
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    rating = serializers.FloatField(read_only=True)
    author = serializers.ReadOnlyField(source="author.handle")
    author_id = serializers.ReadOnlyField(source="author.id")
    banner_image_url = serializers.SerializerMethodField("get_image_url")

    class Meta:
        model = CocktailRecipe
        fields = [
            "name",
            "author",
            "author_id",
            "banner_image_url",
            "category",
            "rating",
            "ingredients",
            "instructions",
        ]

    def get_image_url(self, obj):
        if not obj.banner_image_url:
            return None

        # If it's already a full external URL (e.g., https://example.com/img.jpg), return as-is
        if obj.banner_image_url.startswith(("http://", "https://")):
            return obj.banner_image_url

        # Build absolute URL using current request host (http://127.0.0.1:8000/media/...)
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_url(obj.banner_image_url)


class UploadedImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(method_name="get_url", read_only=True)

    class Meta:
        model = UploadedImage
        fields = [
            "id",
            "url",
            "uploaded_at",
        ]
        read_only_fields = fields

    def get_url(self, obj):
        request = self.context["request"]
        if obj.image and request is not None:
            url = obj.image.url
            absolute_url = request.build_absolute_uri(url)
            return absolute_url
        return None
