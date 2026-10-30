from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User_model = get_user_model()


class UsertsOperationsTests(APITestCase):
    fixtures = ["initial_data.json"]

    @classmethod
    def setUpTestData(cls):
        cls.cocktails_list = reverse("cocktails-list")
        cls.cocktails_detail = lambda id: reverse("cocktails-detail", kwargs={"id": id})
        return super().setUpTestData()

    def test_anonymous_cocktail_list(self):
        response = self.client.get(self.cocktails_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 30)
        self.assertEqual(response.data["results"][0]["name"], "Mojito")

    def test_cocktail_list_filters(self):
        response = self.client.get(
            self.cocktails_list,
            data={"is_alcoholic": True, "ingredients_names": "Cola"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
