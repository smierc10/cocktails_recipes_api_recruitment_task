from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User_model = get_user_model()


class UsertsOperationsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.normal_user_1 = User_model.objects.create_user(
            username="normal_user_1",
            email="normal_user_1@example.com",
            handle="normal_user_1",
            password="Test1234",
        )
        cls.normal_user_2 = User_model.objects.create_user(
            username="normal_user_2",
            email="normal_user_2@example.com",
            handle="normal_user_2",
            password="Test1234",
        )
        cls.staff_user = User_model.objects.create_user(
            username="staff_user",
            email="staff_user@example.com",
            handle="staff_user",
            password="Test1234",
        )
        cls.staff_user.is_staff = True

        cls.user_detail_url = lambda user_handle: reverse(
            "user-detail", kwargs={"handle": user_handle}
        )
        cls.list_url = reverse("user-list")

    def test_regular_user_can_update_own_profile(self):
        self.client.force_authenticate(user=self.normal_user_1)
        payload = {"username": "Test"}
        response = self.client.patch(
            self.user_detail_url(self.normal_user_1.handle), data=payload
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user_1.refresh_from_db()
        self.assertEqual(self.normal_user_1.username, "Test")

    def test_regular_user_can_edit_other_profile(self):
        self.client.force_authenticate(user=self.normal_user_1)
        payload = {"username": "Test"}
        response = self.client.patch(
            self.user_detail_url(self.normal_user_2.handle), data=payload
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_edit_any_profile(self):
        self.client.force_authenticate(user=self.staff_user)
        payload = {"username": "Test"}
        response = self.client.patch(
            self.user_detail_url(self.normal_user_1.handle), data=payload
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user_1.refresh_from_db()
        self.assertEqual(self.normal_user_1.username, "Test")

    def test_staff_remove_any_profile(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(self.user_detail_url(self.normal_user_1.handle))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            User_model.objects.filter(handle=self.normal_user_1.handle).exists()
        )

    def test_anonymous_account_creation(self):
        response = self.client.post(
            self.list_url,
            data={
                "username": "Test",
                "handle": "Test",
                "password": "abcd1234",
                "email": "email@example.com",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User_model.objects.all().count(), 4)
