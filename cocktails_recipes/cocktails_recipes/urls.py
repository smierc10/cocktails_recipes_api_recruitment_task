"""
URL configuration for coctails_recipes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from rest_framework_nested import routers
from cocktails import views
from users import views as users_views

router = routers.DefaultRouter()
router.register("cocktails", views.CocktailRecipeViewSet, basename="cocktails")
user_router = routers.DefaultRouter()
user_router.register("users", users_views.UserViewSet, basename="user")

cocktails_router = routers.NestedSimpleRouter(router, "cocktails", lookup="cocktails")
cocktails_router.register("reviews", views.CocktailReviewsViewSet)

router.register("ingredients", views.IngredientView, basename="ingredient")

urlpatterns = [
    path("", include(user_router.urls)),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include(router.urls)),
    path("api/", include(cocktails_router.urls)),
    # api documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/upload_image", views.UploadedImageView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
