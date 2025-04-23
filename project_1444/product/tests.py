from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from product.models import Product, Descriptions, Categories
from django.utils import timezone
from parler.utils.context import switch_language


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
        print("POST", response.data)
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
        print("PUT en", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], data_en["name"])
        self.assertEqual(response.data["slug"], data_en["slug"])

        print("Translations:", Categories.objects.get(pk=pk).translations.all())

        HTTP_ACCEPT_LANGUAGE = "uk"
        response = self.client.get(
            reverse("categories-detail", args=[pk]),
            HTTP_ACCEPT_LANGUAGE=HTTP_ACCEPT_LANGUAGE,
        )
        print("GET uk", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], data_uk["name"])
        self.assertEqual(response.data["slug"], data_uk["slug"])

        HTTP_ACCEPT_LANGUAGE = "en"
        response = self.client.get(
            reverse("categories-detail", args=[pk]),
            HTTP_ACCEPT_LANGUAGE=HTTP_ACCEPT_LANGUAGE,
        )
        print("GET en", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], data_en["name"])
        self.assertEqual(response.data["slug"], data_en["slug"])


# class ProductAPITestCase(APITestCase):


#     def setUp(self):
#         # Налаштування клієнта для API-запитів
#         self.client = APIClient()
#
#         # Створюємо категорію
#         self.category = Categories.objects.create(
#             name="Кольє",
#             slug="kolie",
#         )
#
#         # Створюємо тестову модель Descriptions
#         self.description = Descriptions.objects.create()
#
#         # Додаємо український переклад
#         with switch_language(self.description, "uk"):
#             self.description.name = "Кольє Francelli"
#             self.description.text = "Золоте кольє Francelli — ультрамодна прикраса..."
#             self.description.slug = "kolie-francelli"
#             self.description.save()
#
#         # Додаємо англійський переклад
#         with switch_language(self.description, "en"):
#             self.description.name = "Francelli Necklace"
#             self.description.text = "The Francelli gold necklace is an ultra-fashionable accessory..."
#             self.description.slug = "francelli-necklace"
#             self.description.save()
#
#         # Створюємо тестовий продукт
#         self.product = Product.objects.create(
#             name="Кольє",
#             category=self.category,  # Передаємо екземпляр Categories
#             subcategory="Кольє",
#             slug="kolie-francelli",
#             sku="SKU-123",
#             article="ART-123",
#             year_collection=2024,
#         )
#         self.product.description.add(self.description)
#
#     def test_products_api_uk_language(self):
#         # Тест для української мови
#         response = self.client.get(
#             reverse('product-list'),
#             HTTP_ACCEPT_LANGUAGE='uk'
#         )
#
#         # Перевіряємо статус відповіді
#         self.assertEqual(response.status_code, 200)
#
#         # Перевіряємо, що повертається український переклад
#         data = response.json()
#         self.assertEqual(len(data), 1)  # Очікуємо один продукт
#         description = data[0]['description'][0]
#         self.assertEqual(description['name'], "Кольє Francelli")
#         self.assertEqual(description['slug'], "kolie-francelli")
#         self.assertTrue(description['text'].startswith("Золоте кольє Francelli"))
#
#     def test_products_api_en_language(self):
#         # Тест для англійської мови
#         response = self.client.get(
#             reverse('product-list'),
#             HTTP_ACCEPT_LANGUAGE='en'
#         )
#
#         # Перевіряємо статус відповіді
#         self.assertEqual(response.status_code, 200)
#
#         # Перевіряємо, що повертається англійський переклад
#         data = response.json()
#         self.assertEqual(len(data), 1)
#         description = data[0]['description'][0]
#         self.assertEqual(description['name'], "Francelli Necklace")
#         self.assertEqual(description['slug'], "francelli-necklace")
#         self.assertTrue(description['text'].startswith("The Francelli gold necklace"))
