from django.shortcuts import render
from rest_framework import permissions, viewsets
from rest_framework import mixins, generics

from .models import User
from .serializers import (
    UserPublicSerializer,
    UserRegisterSerializer,
    UserUpdateSerializer,
)
from .permissions import IsSelfOrStaff


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    http_method_names = ["get", "post", "patch", "delete"]

    lookup_field = "handle"

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "destroy"]:
            return UserPublicSerializer
        elif self.action in ["create", "update"]:
            return UserRegisterSerializer
        elif self.action == "partial_update":
            return UserUpdateSerializer
        return UserPublicSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [permissions.AllowAny()]
        elif self.action in ["partial_update", "destroy"]:
            return [IsSelfOrStaff()]
        return [permissions.IsAdminUser()]
