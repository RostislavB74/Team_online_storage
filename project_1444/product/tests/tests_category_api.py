from rest_framework.test import APIClient, APITestCase
from django.urls import reverse


class CategoriesAPITestCase(APITestCase):
    def setUp(self):
        # Налаштування клієнта для API-запитів
        self.client = APIClient()

    def test_categories_list_api(self):
        # Тестуємо API-запит на отримання списку категорій
        response = self.client.get(reverse("categories-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_categories_create_api_uk(self):
        # Тестуємо API-запит на створення категорії
        data = {
            "name": "Кольє",
            "slug": "kolie",
        }
        headers = {"HTTP_ACCEPT_LANGUAGE": "uk"}
        response = self.client.post(reverse("categories-list"), data, headers=headers)
        # print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Кольє")
        self.assertEqual(response.data["slug"], "kolie")

    def test_categories_create_api_en(self):
        # Тестуємо API-запит на створення категорії
        data = {
            "name": "kolie",
            "slug": "kolie",
        }
        headers = {"HTTP_ACCEPT_LANGUAGE": "en"}
        response = self.client.post(reverse("categories-list"), data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "kolie")
        self.assertEqual(response.data["slug"], "kolie")

    def test_categories_create_api_update(self):
        # Тестуємо API-запит на створення категорії
        data_uk = {
            "name": "Кольє",
            "slug": "kolie_uk",
        }
        HTTP_ACCEPT_LANGUAGE = "uk"
        response = self.client.post(
            reverse("categories-list"),
            data_uk,
            HTTP_ACCEPT_LANGUAGE=HTTP_ACCEPT_LANGUAGE,
        )
        # print("POST", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], data_uk["name"])
        self.assertEqual(response.data["slug"], data_uk["slug"])

        pk = response.data["id"]

        data_en = {
            "name": "kolie_en",
            "slug": "kolie_en",
        }
        HTTP_ACCEPT_LANGUAGE = "en"
        response = self.client.put(
            reverse("categories-detail", args=[pk]),
            data_en,
            HTTP_ACCEPT_LANGUAGE=HTTP_ACCEPT_LANGUAGE,
        )
        # print("PUT en", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], data_en["name"])
        self.assertEqual(response.data["slug"], data_en["slug"])

        # print("Translations:", Categories.objects.get(pk=pk).translations.all())

        HTTP_ACCEPT_LANGUAGE = "uk"
        response = self.client.get(
            reverse("categories-detail", args=[pk]),
            HTTP_ACCEPT_LANGUAGE=HTTP_ACCEPT_LANGUAGE,
        )
        # print("GET uk", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], data_uk["name"])
        self.assertEqual(response.data["slug"], data_uk["slug"])

        HTTP_ACCEPT_LANGUAGE = "en"
        response = self.client.get(
            reverse("categories-detail", args=[pk]),
            HTTP_ACCEPT_LANGUAGE=HTTP_ACCEPT_LANGUAGE,
        )
        # print("GET en", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], data_en["name"])
        self.assertEqual(response.data["slug"], data_en["slug"])

    def test_categories_create_api_delete(self):
        # Тестуємо API-запит на створення категорії
        data_uk = {
            "name": "Кольє",
            "slug": "kolie_uk",
        }
        HTTP_ACCEPT_LANGUAGE = "uk"
        response = self.client.post(
            reverse("categories-list"),
            data_uk,
            HTTP_ACCEPT_LANGUAGE=HTTP_ACCEPT_LANGUAGE,
        )
        # print("POST", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], data_uk["name"])
        self.assertEqual(response.data["slug"], data_uk["slug"])

        pk = response.data["id"]

        HTTP_ACCEPT_LANGUAGE = "uk"
        response = self.client.delete(
            reverse("categories-detail", args=[pk]),
            HTTP_ACCEPT_LANGUAGE=HTTP_ACCEPT_LANGUAGE,
        )
        # print("DELETE", response.data)
        self.assertEqual(response.status_code, 204)

        response = self.client.get(
            reverse("categories-detail", args=[pk]),
            HTTP_ACCEPT_LANGUAGE=HTTP_ACCEPT_LANGUAGE,
        )
        # print("GET", response.data)
        self.assertEqual(response.status_code, 404)
