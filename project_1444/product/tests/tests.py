from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from product.models import Product, Descriptions, Categories, SubProducts
from users.models import User
from django.utils.text import slugify


class ProductAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Створюємо категорію
        self.category = Categories()
        self.category.set_current_language("uk")
        self.category.name = "Кільця"
        self.category.slug = slugify("Кільця") + "-cat"
        self.category.save()

        # Створюємо описи
        self.description1 = Descriptions()
        self.description1.set_current_language("uk")
        self.description1.name = "Опис золотого кільця"
        self.description1.text = "Гарне золоте кільце"
        self.description1.slug = slugify("Опис золотого кільця") + "-1"
        self.description1.save()

        self.description2 = Descriptions()
        self.description2.set_current_language("uk")
        self.description2.name = "Опис срібного кільця"
        self.description2.text = "Срібна прикраса"
        self.description2.slug = slugify("Опис срібного кільця") + "-2"
        self.description2.save()

        # Створюємо продукти
        self.product1 = Product(
            category=self.category, created_by=self.user, article="ART001", sku="SKU001"
        )
        self.product1.set_current_language("uk")
        self.product1.name = "Золоте кільце"
        self.product1.slug = slugify("Золоте кільце") + "-1"
        self.product1.save()
        self.product1.description.add(self.description1)

        self.product2 = Product(
            category=self.category, created_by=self.user, article="ART002", sku="SKU002"
        )
        self.product2.set_current_language("uk")
        self.product2.name = "Срібне кільце"
        self.product2.slug = slugify("Срібне кільце") + "-2"
        self.product2.save()
        self.product2.description.add(self.description2)

        # Створюємо SubProducts
        self.subproduct1 = SubProducts(
            parent_product=self.product1,
            price=1500,
            article="SUBART001",
            sku="SUBSKU001",
        )
        self.subproduct1.save()
        self.product1.subproducts.add(self.subproduct1)

        self.subproduct2 = SubProducts(
            parent_product=self.product2,
            price=3000,
            article="SUBART002",
            sku="SUBSKU002",
        )
        self.subproduct2.save()
        self.product2.subproducts.add(self.subproduct2)

    def test_search_by_name(self):
        response = self.client.get(
            reverse("product-list"), {"name": "кільце", "lang": "uk"}
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()
        # Адаптація до можливої непагінованої відповіді
        if isinstance(results, dict) and "results" in results:
            results = results["results"]
        self.assertEqual(len(results), 2, f"Expected 2 results, got {len(results)}")
        self.assertIn("Золоте кільце", [item["name"] for item in results])
        self.assertIn("Срібне кільце", [item["name"] for item in results])

    def test_search_by_description(self):
        response = self.client.get(
            reverse("product-list"), {"name": "золоте", "lang": "uk"}
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()
        if isinstance(results, dict) and "results" in results:
            results = results["results"]
        self.assertEqual(len(results), 1, f"Expected 1 result, got {len(results)}")
        self.assertEqual(results[0]["name"], "Золоте кільце")

    def test_filter_and_ordering(self):
        response = self.client.get(
            reverse("product-list"),
            {
                "categories": str(self.category.id),
                "price_min": 1000,
                "price_max": 2000,
                "ordering": "-subproducts__price",
                "lang": "uk",
            },
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()
        if isinstance(results, dict) and "results" in results:
            results = results["results"]
        self.assertEqual(len(results), 1, f"Expected 1 result, got {len(results)}")
        self.assertEqual(results[0]["name"], "Золоте кільце")

    def test_etag(self):
        response = self.client.get(reverse("product-list"), {"lang": "uk"})
        etag = response.headers.get("ETag")
        self.assertIsNotNone(etag)
        response = self.client.get(
            reverse("product-list"), {"lang": "uk"}, HTTP_IF_NONE_MATCH=etag
        )
        self.assertEqual(response.status_code, 304)

    