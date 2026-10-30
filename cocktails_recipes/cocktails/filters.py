import django_filters
from .models import CocktailRecipe


class CocktailRecipesFilter(django_filters.FilterSet):
    ingredients_ids = django_filters.CharFilter(method="filter_by_ingredients_id")
    ingredients_names = django_filters.CharFilter(method="filter_by_ingredients_name")

    is_alcoholic = django_filters.BooleanFilter(method="filter_is_alcoholic")
    is_vegan = django_filters.BooleanFilter(method="filter_is_vegan")
    category = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )
    name = django_filters.CharFilter(lookup_expr="icontains")
    name_exact = django_filters.CharFilter(field_name="name", lookup_expr="iexact")

    author_handle = django_filters.CharFilter(
        field_name="author__handle", lookup_expr="iexact"
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("rating", "rating"),
        ),
    )

    class Meta:
        model = CocktailRecipe
        fields = ["name", "name_exact", "category", "author_handle"]

    def filter_by_ingredients_id(self, queryset, name, value):
        filtering_ingredients_id = [
            id.strip() for id in value.split(",") if id.strip() != ""
        ]

        for ingredient_id in filtering_ingredients_id:
            queryset = queryset.filter(recipeingredient__ingredient__id=ingredient_id)

        return queryset.distinct()

    def filter_by_ingredients_name(self, queryset, name, value):
        filtering_ingredients_id = [
            name.strip() for name in value.split(",") if name.strip() != ""
        ]

        for ingredient_id in filtering_ingredients_id:
            queryset = queryset.filter(recipeingredient__ingredient__name=ingredient_id)

        return queryset.distinct()

    def filter_is_alcoholic(self, queryset, name, value):
        if value is True:
            return queryset.filter(
                recipeingredient__ingredient__is_alcoholic=True
            ).distinct()
        if value is False:
            # Wykluczamy wszystkie przepisy, które mają choćby jeden alkoholowy składnik
            return queryset.exclude(
                recipeingredient__ingredient__is_alcoholic=True
            ).distinct()
        return queryset

    def filter_is_vegan(self, queryset, name, value):
        if value is True:
            return queryset.filter(
                recipeingredient__ingredient__is_vegan=True
            ).distinct()
        if value is False:
            # Wykluczamy wszystkie przepisy, które mają choćby jeden alkoholowy składnik
            return queryset.exclude(
                recipeingredient__ingredient__is_vegan=True
            ).distinct()
        return queryset
