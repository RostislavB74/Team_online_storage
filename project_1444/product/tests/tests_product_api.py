from django.conf import settings
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from product.models import Product, Descriptions, Categories, SubCategories
from parler.utils.context import switch_language


class ProductAPITestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # Don't forget this!
        cls.client = APIClient()
        cls.crud()

    @classmethod
    def tearDownClass(cls):
        if getattr(settings, "SAVE_TEST_DB_OUTPUT", False):
            from django.core.management import call_command

            dump_file = f"test_db_output_{cls.__name__}.json"
            with open(dump_file, "w", encoding="utf-8") as f:
                call_command("dumpdata", indent=2, stdout=f)
            print(f"Dumped test data to: {dump_file}")
        super().tearDownClass()

    @staticmethod
    def crud():
        print("CRUD")
        # Створюємо об'єкти через прямий доступ до моделі
        if Categories.objects.exists():
            print("Categories already exist, skip CRUD")
            return

        category = Categories.objects.create(
            name="Кольє",
            slug="kolie",
        )
        with switch_language(category, "en"):
            category.name = "Necklace"
            category.slug = "necklace"
            category.save()

        # add subcategory
        subcategory = SubCategories.objects.create(
            name="Кольє_тип1",
            slug="kolie_type1",
            parent=category,
        )
        with switch_language(subcategory, "en"):
            category.name = "Necklace_type1"
            category.slug = "necklace_type1"
            category.save()

        # Створюємо тестову модель Descriptions
        description = Descriptions.objects.create()

        # Додаємо український переклад
        with switch_language(description, "uk"):
            description.name = "Кольє Francelli"
            description.text = "Золоте кольє Francelli — ультрамодна прикраса..."
            description.slug = "kolie-francelli"
            description.save()

        # Додаємо англійський переклад
        with switch_language(description, "en"):
            description.name = "Francelli Necklace"
            description.text = (
                "The Francelli gold necklace is an ultra-fashionable accessory..."
            )
            description.slug = "francelli-necklace"
            description.save()

        # Створюємо тестовий продукт
        product = Product.objects.create(
            name="Кольє",
            category=category,  # Передаємо екземпляр Categories
            subcategory=subcategory,
            slug="kolie-francelli",
            sku="SKU-123",
            article="ART-123",
            year_collection=2024,
        )
        product.description.add(description)

        with switch_language(product, "en"):
            product.name = "Francelli Necklace"
            product.slug = "francelli-necklace"
            product.save()

        print("CRUD product:", product)

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
