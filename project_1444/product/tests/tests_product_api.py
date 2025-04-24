from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from product.models import Product, Descriptions, Categories
from parler.utils.context import switch_language


class ProductAPITestCase(APITestCase):

    def setUp(self):
        # Налаштування клієнта для API-запитів
        self.client = APIClient()

        # Створюємо категорію
        self.category = Categories.objects.create(
            name="Кольє",
            slug="kolie",
        )

        # Створюємо тестову модель Descriptions
        self.description = Descriptions.objects.create()

        # Додаємо український переклад
        with switch_language(self.description, "uk"):
            self.description.name = "Кольє Francelli"
            self.description.text = "Золоте кольє Francelli — ультрамодна прикраса..."
            self.description.slug = "kolie-francelli"
            self.description.save()

        # Додаємо англійський переклад
        with switch_language(self.description, "en"):
            self.description.name = "Francelli Necklace"
            self.description.text = (
                "The Francelli gold necklace is an ultra-fashionable accessory..."
            )
            self.description.slug = "francelli-necklace"
            self.description.save()

        # Створюємо тестовий продукт
        self.product = Product.objects.create(
            name="Кольє",
            category=self.category,  # Передаємо екземпляр Categories
            subcategory="Кольє",
            slug="kolie-francelli",
            sku="SKU-123",
            article="ART-123",
            year_collection=2024,
        )
        self.product.description.add(self.description)

    def test_products_api_uk_language(self):
        # Тест для української мови
        response = self.client.get(reverse("product-list"), HTTP_ACCEPT_LANGUAGE="uk")

        # Перевіряємо статус відповіді
        self.assertEqual(response.status_code, 200)

        # Перевіряємо, що повертається український переклад
        data = response.json()
        self.assertEqual(len(data), 1)  # Очікуємо один продукт
        description = data[0]["description"][0]
        self.assertEqual(description["name"], "Кольє Francelli")
        self.assertEqual(description["slug"], "kolie-francelli")
        self.assertTrue(description["text"].startswith("Золоте кольє Francelli"))

    def test_products_api_en_language(self):
        # Тест для англійської мови
        response = self.client.get(reverse("product-list"), HTTP_ACCEPT_LANGUAGE="en")

        # Перевіряємо статус відповіді
        self.assertEqual(response.status_code, 200)

        # Перевіряємо, що повертається англійський переклад
        data = response.json()
        self.assertEqual(len(data), 1)
        description = data[0]["description"][0]
        self.assertEqual(description["name"], "Francelli Necklace")
        self.assertEqual(description["slug"], "francelli-necklace")
        self.assertTrue(description["text"].startswith("The Francelli gold necklace"))
