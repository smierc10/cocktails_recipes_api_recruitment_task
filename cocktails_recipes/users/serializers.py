from rest_framework import serializers
from .models import User


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "handle"]


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "is_staff"]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        instance = super().update(instance, validated_data)

        if password is not None:
            instance.set_password(password)
            instance.save()

        return instance

    def validate(self, attrs):
        request = self.context.get("request")

        if attrs.get("is_staff") is True:
            if (
                not request
                or not request.user.is_authenticated
                or not request.user.is_staff
            ):
                raise serializers.ValidationError(
                    {"is_staff": "Nie masz uprawnień do zmiany statusu administratora"}
                )

        return attrs


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "handle", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            handle=validated_data["handle"].lower(),
        )

        return user
