from http import HTTPStatus

from django.conf import settings
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse


class CategoriesAPITestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # Don't forget this!
        cls.client = APIClient()
        cls.crud()

    @classmethod
    def crud(cls):
        # print("CRUD")
        cls.create_superuser()

    @classmethod
    def tearDownClass(cls):
        if getattr(settings, "SAVE_TEST_DB_OUTPUT", False):
            from django.core.management import call_command

            dump_file = f"test_db_output_{cls.__name__}.json"
            with open(dump_file, "w", encoding="utf-8") as f:
                call_command("dumpdata", indent=2, stdout=f)
            # print(f"Dumped test data to: {dump_file}")
        super().tearDownClass()

    @classmethod
    def create_superuser(cls):
        from django.contrib.auth.models import User

        cls.user = User.objects.create_superuser(username="admin", password="admin")
        # self.client.force_login(user=self.user)

    def setUp(self):
        # Налаштування клієнта для API-запитів
        # self.client = APIClient()
        # works as Anonymous client
        self.logout()

    def login(self):
        self.client.force_login(user=self.user)

    def logout(self):
        self.client.logout()

    def test_test_categories_create_api_authorization(self):
        self.logout()
        data = {
            "name": "Кольє_auth",
            "slug": "kolie_auth",
        }
        http_accept_language = "uk"
        response = self.client.post(
            reverse("categories-list"), data, HTTP_ACCEPT_LANGUAGE=http_accept_language
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.login()
        response = self.client.post(
            reverse("categories-list"), data, HTTP_ACCEPT_LANGUAGE=http_accept_language
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["slug"], data["slug"])

    def test_categories_list_api(self):
        # Тестуємо API-запит на отримання списку категорій
        response = self.client.get(reverse("categories-list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.data), 0)

    def test_categories_create_api_uk(self):
        # Тестуємо API-запит на створення категорії
        self.login()
        data = {
            "name": "Кольє",
            "slug": "kolie",
        }
        http_accept_language = "uk"
        response = self.client.post(
            reverse("categories-list"), data, HTTP_ACCEPT_LANGUAGE=http_accept_language
        )
        # print(response.data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.data["name"], "Кольє")
        self.assertEqual(response.data["slug"], "kolie")

    def test_categories_create_api_en(self):
        # Тестуємо API-запит на створення категорії
        self.login()
        data = {
            "name": "kolie",
            "slug": "kolie",
        }
        http_accept_language = "uk"
        response = self.client.post(
            reverse("categories-list"), data, HTTP_ACCEPT_LANGUAGE=http_accept_language
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.data["name"], "kolie")
        self.assertEqual(response.data["slug"], "kolie")

    def test_categories_create_api_update(self):
        # Тестуємо API-запит на створення категорії
        self.login()
        data_uk = {
            "name": "Кольє",
            "slug": "kolie_uk",
        }
        http_accept_language = "uk"
        response = self.client.post(
            reverse("categories-list"),
            data_uk,
            HTTP_ACCEPT_LANGUAGE=http_accept_language,
        )
        # print("POST", response.data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.data["name"], data_uk["name"])
        self.assertEqual(response.data["slug"], data_uk["slug"])

        pk = response.data["id"]

        data_en = {
            "name": "kolie_en",
            "slug": "kolie_en",
        }
        http_accept_language = "en"
        response = self.client.put(
            reverse("categories-detail", args=[pk]),
            data_en,
            HTTP_ACCEPT_LANGUAGE=http_accept_language,
        )
        # print("PUT en", response.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["name"], data_en["name"])
        self.assertEqual(response.data["slug"], data_en["slug"])

        # print("Translations:", Categories.objects.get(pk=pk).translations.all())

        http_accept_language = "uk"
        response = self.client.get(
            reverse("categories-detail", args=[pk]),
            HTTP_ACCEPT_LANGUAGE=http_accept_language,
        )
        # print("GET uk", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], data_uk["name"])
        self.assertEqual(response.data["slug"], data_uk["slug"])

        http_accept_language = "en"
        response = self.client.get(
            reverse("categories-detail", args=[pk]),
            HTTP_ACCEPT_LANGUAGE=http_accept_language,
        )
        # print("GET en", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], data_en["name"])
        self.assertEqual(response.data["slug"], data_en["slug"])

    def test_categories_create_api_delete(self):
        # Тестуємо API-запит на створення категорії
        self.login()
        data_uk = {
            "name": "Кольє",
            "slug": "kolie_uk",
        }
        http_accept_language = "uk"
        response = self.client.post(
            reverse("categories-list"),
            data_uk,
            HTTP_ACCEPT_LANGUAGE=http_accept_language,
        )
        # print("POST", response.data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.data["name"], data_uk["name"])
        self.assertEqual(response.data["slug"], data_uk["slug"])

        pk = response.data["id"]

        http_accept_language = "uk"
        response = self.client.delete(
            reverse("categories-detail", args=[pk]),
            HTTP_ACCEPT_LANGUAGE=http_accept_language,
        )
        # print("DELETE", response.data)
        self.assertEqual(response.status_code, 204)

        response = self.client.get(
            reverse("categories-detail", args=[pk]),
            HTTP_ACCEPT_LANGUAGE=http_accept_language,
        )
        # print("GET", response.data)
        self.assertEqual(response.status_code, 404)
