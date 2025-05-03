import logging
import random
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient

logger = logging.getLogger(__name__)

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
        logger.debug("Generated test user:", cls.user_test)
        cls.crud()

    @classmethod
    def create_superuser(cls):
        cls.user = User.objects.create_superuser(username="admin", password="admin")
        logger.debug("Created superuser:", cls.user)

    @classmethod
    def crud(cls):
        # print("CRUD")
        cls.create_superuser()

    def login(self, user: User):
        self.client.force_login(user=user)

    def logout(self):
        self.client.logout()

    def get_user_by_id(self, user_id: int) -> User | None:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def create_user_unit(
        self,
        username: str,
        password: str | None = None,
        email: str = None,
        is_active: bool = True,
    ):
        assert username, "Username is required"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=is_active,
        )
        logger.debug("Created user:", user)
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
            # print("Extracted OTP:", otp_code)
        return otp_code

    def verify_otp_code_request(self, otp_code: str, otp_user_id: int) -> bool:
        data: dict = {"otp_code": otp_code, "otp_user_id": otp_user_id}
        response = self.client.post(reverse("api_verify_otp"), data, format="json")
        # print("POST", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("status"), "success")
        assert response.data.get("token"), "Token should not be returned"
        self.assertEqual(response.data.get("user_id"), otp_user_id)
        return True

    def test_login_user(self):
        user = self.create_user_unit(**self.user_test)
        assert user, "Test user is not created"
        data = {
            "username": self.user_test["username"],
            "password": self.user_test["password"],
        }
        otp_code = None
        with mock.patch("users.views.send_email_in_background") as mock_send_mail:
            mock_send_mail.return_value = None
            response = self.client.post(reverse("api_login"), data, format="json")
            assert mock_send_mail.called, "Email was not sent!"
            # print("Mock args:", mock_send_mail.call_args)
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
            self.assertIn(user.email, recipient_list, "Email is not in recipient list")
        verified_otp = self.verify_otp_code_request(otp_code, user.pk)
        self.assertTrue(verified_otp, "OTP code is not valid")
        # print("POST", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "otp_sent")
        self.assertEqual(response.data["otp_user_id"], user.pk)

    def test_register_user(self):
        data: dict = {
            "username": self.user_test["username"],
            "password": self.user_test["password"],
            "password_confirm": self.user_test["password"],
            "email": self.user_test["email"],
        }
        otp_code = None
        with mock.patch("users.views.send_email_in_background") as mock_send_mail:
            mock_send_mail.return_value = None
            response = self.client.post(reverse("api_register"), data, format="json")
            user_id = response.data.get("user_id")
            self.assertGreater(user_id, 1, "User ID should be greater than 1")
            assert mock_send_mail.called, "Email was not sent!"
            # print("Mock args:", mock_send_mail.call_args)
            # Unpack arguments
            kwargs = mock_send_mail.call_args.kwargs  # or call_args[1]
            message = kwargs["message"]
            otp_code = self.extract_otp_code(message)
            assert otp_code, "OTP code is not extracted"
            user = self.get_user_by_id(user_id)
            self.assertIsNotNone(user, "User is not created")
            self.assertEqual(user.username, self.user_test["username"])
            self.assertEqual(user.email, self.user_test["email"])
            self.assertFalse(user.is_active, "User should not be active")

        # print("POST", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get("status"), "otp_sent", "Status should be otp_sent"
        )
        self.assertEqual(
            response.data.get("username"),
            self.user_test["username"],
            "Username should be the same",
        )
        self.assertIsNone(response.data.get("token"), "Token should not be returned")
        # Verify OTP
        verified_otp = self.verify_otp_code_request(otp_code, user_id)
        self.assertTrue(verified_otp, "OTP code is not valid")
        user = self.get_user_by_id(user_id)
        self.assertTrue(user.is_active, "User should be active")

    def test_get_token(self):
        user = self.create_user_unit(**self.user_test)
        assert user, "Test user is not created"
        data = {
            "username": self.user_test["username"],
            "password": self.user_test["password"],
        }

        response = self.client.post(reverse("api_token"), data, format="json")
        # print("POST", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data.get("token")
        assert token, "Token shouldbe returned"
        assert len(token) > 30, "Token should be not shorter than 30 characters"
