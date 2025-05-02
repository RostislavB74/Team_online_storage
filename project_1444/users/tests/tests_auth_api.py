import random
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient


User = get_user_model()


class AuthAPITest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # Don't forget this!

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user_test = {
            "username": "test_user",
            "password": get_random_string(10),
            "email": f"test_user{random.randint(1, 100)}@test.com",
        }
        print("Generated test user:", cls.user_test)
        cls.crud()

    @classmethod
    def create_superuser(cls):
        cls.user = User.objects.create_superuser(username="admin", password="admin")
        print("Created superuser:", cls.user)

    @classmethod
    def crud(cls):
        # print("CRUD")
        cls.create_superuser()

    def login(self, user: User):
        self.client.force_login(user=user)

    def logout(self):
        self.client.logout()

    def create_user_unit(
        self, username: str, password: str | None = None, email: str = None
    ):
        assert username, "Username is required"
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        print("Created user:", user)
        return user

    def setUp(self):
        # Logout before each test
        self.logout()

    def extract_otp_code(self, message) -> str | None:
        # Extract from plain text message
        otp_code = None
        otp_code_match = message.split()[-1]
        if otp_code_match.isnumeric():
            otp_code = otp_code_match
            print("Extracted OTP:", otp_code)
        return otp_code

    def test_login_user(self):
        user = self.create_user_unit(**self.user_test)
        assert user, "Test user is not created"
        data = {
            "username": self.user_test["username"],
            "password": self.user_test["password"],
        }
        otp_code = None
        with mock.patch("users.views.send_mail") as mock_send_mail:
            mock_send_mail.return_value = None
            response = self.client.post(reverse("api_login"), data, format="json")

            print("Mock args:", mock_send_mail.call_args)
            # Unpack arguments
            kwargs = mock_send_mail.call_args.kwargs  # or call_args[1]
            subject = kwargs["subject"]
            message = kwargs["message"]
            from_email = kwargs["from_email"]
            recipient_list = kwargs["recipient_list"]
            otp_code = self.extract_otp_code(message)
            assert "otp" in subject.lower()
            assert otp_code, "OTP code is not extracted"
            self.assertEqual(len(otp_code), 6, "OTP code should be 6 digits")
            assert user.email in recipient_list, "Email is not in recipient list"

        print("POST", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "otp_sent")
        self.assertEqual(response.data["message"], "OTP sent to your email")
        self.assertEqual(response.data["otp_user_id"], user.pk)
