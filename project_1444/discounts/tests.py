# from django.test import TestCase
# from rest_framework.test import APIClient, APITestCase
# from django.urls import reverse
# from product.models import Product, Descriptions, Categories, SubProducts
# from users.models import UserProfile
# from discounts.models import PersonalDiscount
# from django.utils import timezone
# from parler.utils.context import switch_language
# from django.contrib.auth.models import User
# from django.utils.timezone import now, timedelta

# class ProductAPITestCase(APITestCase):
#     def setUp(self):
#         self.client = APIClient()

#         # Створюємо користувача і профіль
#         self.user = User.objects.create_user(username="testuser", password="testpass")
#         self.profile = UserProfile.objects.create(user=self.user)

#         # Створюємо категорію
#         self.category = Categories.objects.create(name="Кольє", slug="kolie")

#         # Створюємо опис
#         self.description = Descriptions.objects.create()
#         with switch_language(self.description, "uk"):
#             self.description.name = "Кольє Francelli"
#             self.description.text = "Золоте кольє Francelli..."
#             self.description.slug = "kolie-francelli"
#             self.description.save()
#         with switch_language(self.description, "en"):
#             self.description.name = "Francelli Necklace"
#             self.description.text = "The Francelli gold necklace..."
#             self.description.slug = "francelli-necklace"
#             self.description.save()

#         # Створюємо продукт
#         self.product = Product.objects.create(
#             name="Кольє",
#             category=self.category,
#             subcategory=None,
#             slug="kolie-francelli",
#             sku="SKU-123",
#             article="ART-123",
#             year_collection=2024,
#             created_by=self.user
#         )
#         self.product.description.add(self.description)

#         # Створюємо субпродукт
#         self.subproduct = SubProducts.objects.create(
#             parent_product=self.product,
#             price=1000.00,
#             sku="SUB-SKU-123",
#             article="SUB-ART-123",
#             created_by=self.user
#         )

#         # Створюємо персональну знижку
#         self.discount = PersonalDiscount.objects.create(
#             profile=self.profile,
#             assigned_by=self.user,
#             discount_percentage=10.00,
#             is_active=True,
#             valid_from=now(),
#             valid_to=now() + timedelta(days=30)
#         )
#         self.discount.applicable_products.add(self.product)
#         # Якщо додали applicable_subproducts:
#         # self.discount.applicable_subproducts.add(self.subproduct)

#     def test_products_api_uk_language(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(
#             reverse('product-list'),
#             HTTP_ACCEPT_LANGUAGE='uk'
#         )
#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertEqual(len(data), 1)
#         description = data[0]['description'][0]
#         self.assertEqual(description['name'], "Кольє Francelli")
#         self.assertEqual(data[0]['new_price'], 900.00)  # 1000 * (100-10)/100
#         self.assertEqual(data[0]['discount_applied'], 10.00)

#     def test_products_api_en_language(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(
#             reverse('product-list'),
#             HTTP_ACCEPT_LANGUAGE='en'
#         )
#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertEqual(len(data), 1)
#         description = data[0]['description'][0]
#         self.assertEqual(description['name'], "Francelli Necklace")
#         self.assertEqual(data[0]['new_price'], 900.00)
#         self.assertEqual(data[0]['discount_applied'], 10.00)
