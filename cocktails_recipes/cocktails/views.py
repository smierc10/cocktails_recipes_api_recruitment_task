from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from django.db.models import Avg

from rest_framework import permissions
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import mixins, generics
from rest_framework import status, viewsets
from rest_framework.views import APIView, Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from django_filters import rest_framework as filters


from .models import CocktailRecipe, Ingredient, Review, UploadedImage
from .permissions import IsAuthorOrStaffOrReadOnly, IsStaffOrReadOnly
from .filters import CocktailRecipesFilter

from .serializers import (
    CocktailRecipeDetailSerializer,
    CocktailRecipeListSerializer,
    CocktailRecipeWriteSerializer,
    IngredientSerializer,
    ReviewWriteSerializer,
    ReviewSerializer,
    UploadedImageSerializer,
)

from .image_utils import verify_and_convert_image


# Create your views here.
@extend_schema(tags=["Cocktails"])
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="ingredients_ids",
                type=OpenApiTypes.STR,
                description="Comma-separated list of ingredient IDs (e.g., 1,2,3).",
            ),
            OpenApiParameter(
                name="ingredients_names",
                type=OpenApiTypes.STR,
                description="Comma-separated list of ingredient names (e.g., Lime,Beer,Tonic).",
            ),
        ]
    )
)
class CocktailRecipeViewSet(viewsets.ModelViewSet):
    filterset_class = CocktailRecipesFilter

    queryset = (
        CocktailRecipe.objects.all()
        .annotate(rating=Avg("review__rating", default=0))
        .order_by("id")
    )
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly]

    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action == "list":
            return CocktailRecipeListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CocktailRecipeWriteSerializer
        else:
            return CocktailRecipeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(request=CocktailRecipeWriteSerializer)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        request=CocktailRecipeListSerializer,
        responses={200: CocktailRecipeDetailSerializer},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        methods=["POST"],
        request=ReviewWriteSerializer,
        responses={201: ReviewSerializer},
        tags=["Reviews"],
    )
    @extend_schema(
        methods=["DELETE"],
        request=ReviewWriteSerializer,
        responses={204: None},
        tags=["Reviews"],
    )
    @extend_schema(
        methods=["PATCH"],
        request=ReviewWriteSerializer,
        responses={200: ReviewSerializer},
        tags=["Reviews"],
    )
    @action(detail=True, methods=["post", "patch", "delete"])
    def review(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == "DELETE":
            try:
                review = Review.objects.get(recipe=recipe, author=user)
                review.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Review.DoesNotExist:
                return Response(
                    {"detail": "Review not found"}, status=status.HTTP_404_NOT_FOUND
                )

        elif request.method == "POST":
            if Review.objects.filter(recipe=recipe, author=user).exists():
                return Response(
                    {
                        "detail": "You have already reviewed this recipe, use PUT to update it."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ReviewWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, author=user)
            # read_serializer = CocktailRecipeDetailSerializer(
            #     recipe, context={"request": request}
            # )
            # # TODO()
            # return Response(read_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "PATCH":
            try:
                review = Review.objects.get(recipe=recipe, author=user)
            except Review.DoesNotExist:
                return Response(
                    {"detail": "Review not found, use POST to create one."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = ReviewWriteSerializer(review, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, author=user)
            return Response(serializer.data)


@extend_schema(tags=["Reviews"])
class CocktailReviewsViewSet(
    mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = Review.objects.all()

    def get_queryset(self):
        return self.queryset.filter(recipe_id=self.kwargs["cocktail_pk"])

    serializer_class = ReviewSerializer

    permission_classes = [IsStaffOrReadOnly]


@extend_schema(tags=["Ingredients"])
class IngredientView(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class UploadedImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *Args, **kwargs):
        if "image" not in request.FILES:
            return Response(
                "attach an image using 'image' field",
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_file = request.FILES["image"]

        try:
            image_in_memory = verify_and_convert_image(image_file)
        except ValueError as e:
            return Response(
                f"provided image files did not pass verification: {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return Response(
                f"PIL returned error during file verification: {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_instance = UploadedImage.objects.create(
            image=image_in_memory, author=request.user
        )
        image_instance.save()
        serializer = UploadedImageSerializer(
            image_instance, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
