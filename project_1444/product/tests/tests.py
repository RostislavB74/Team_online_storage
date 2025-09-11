from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from product.models import Product, Category, Descriptions
from django_parler.utils.context import switch_language


class ProductAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create()
        self.category.set_current_language("uk")
        self.category.name = "Кільця"
        self.category.save()

        self.description = Descriptions.objects.create()
        self.description.set_current_language("uk")
        self.description.text = "Гарне кільце"
        self.description.save()

        self.product = Product.objects.create(
            category=self.category, description=self.description, price=1500
        )
        self.product.set_current_language("uk")
        self.product.name = "Золоте кільце"
        self.product.save()

    def test_search_by_name(self):
        with switch_language(Product, "uk"):
            response = self.client.get(
                reverse("product-list"), {"name": "кільце", "lang": "uk"}
            )
            self.assertEqual(response.status_code, 200)
            results = response.json()["results"]
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["name"], "Золоте кільце")
