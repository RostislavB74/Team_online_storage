# from django.test import TestCase
# from rest_framework.test import APIClient
# from django.contrib.auth.models import User
# from .models import UserProfile, OTP, UserNotificationSettings
# from cart.models import Cart
# from product.models import SubProducts, Product, Categories
# from django.utils import timezone
# from datetime import timedelta
# from rest_framework.authtoken.models import Token
# from django.core.files.uploadedfile import SimpleUploadedFile

# class AuthAPITest(TestCase):
#     def setUp(self):
/*************  ✨ Windsurf Command ⭐  *************/
        """
        Creates a test user, profile, product, subproduct and a cart entry.
        """
/*******  8314059a-4602-424c-af1c-67ae0666f1eb  *******/
#         self.client = APIClient()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.profile = UserProfile.objects.get(user=self.user)
#         self.profile.gender = 'M'
#         self.profile.viber = '380123456789'
#         self.profile.avatar = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
#         self.profile.save()
#         self.notifications = UserNotificationSettings.objects.get(user=self.user)
#         self.category = Categories.objects.create(name='Test', slug='test')
#         self.product = Product.objects.create(name='Test Product', category=self.category, sku='TEST123')
#         self.subproduct = SubProducts.objects.create(parent_product=self.product, price=1000.00, sku='SUB123')
#         Cart.objects.create(user=self.user, product=self.subproduct, quantity=1, session_key='test_session')

#     def test_login_and_otp(self):
#         response = self.client.post('/api/auth/login/', {
#             'username': 'testuser',
#             'password': 'testpass'
#         }, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['status'], 'otp_sent')
#         otp = OTP.objects.filter(user=self.user).first()
#         self.assertIsNotNone(otp)

#         response = self.client.post('/api/verify-otp/', {
#             'otp_code': otp.code,
#             'otp_user_id': self.user.id
#         }, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['status'], 'success')
#         self.assertIn('token', response.data)

#     def test_rate_limit_login(self):
#         for _ in range(5):
#             response = self.client.post('/api/auth/login/', {
#                 'username': 'testuser',
#                 'password': 'wrongpass'
#             }, format='json')
#             self.assertEqual(response.status_code, 400)
#         response = self.client.post('/api/auth/login/', {
#             'username': 'testuser',
#             'password': 'wrongpass'
#         }, format='json')
#         self.assertEqual(response.status_code, 429)
#         self.assertIn('Request limit exceeded', response.data['detail'])

#     def test_register(self):
#         response = self.client.post('/api/auth/register/', {
#             'username': 'newuser',
#             'password': 'newpass123',
#             'password_confirm': 'newpass123'
#         }, format='json')
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.data['status'], 'success')
#         self.assertIn('token', response.data)
#         new_user = User.objects.get(username='newuser')
#         self.assertTrue(hasattr(new_user, 'profile'))
#         self.assertTrue(hasattr(new_user, 'notifications'))

#     def test_profile_update(self):
#         token = Token.objects.create(user=self.user)
#         self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
#         response = self.client.post('/api/profile/', {
#             'gender': 'F',
#             'viber': '380987654321',
#             'avatar': SimpleUploadedFile("new_avatar.jpg", b"new_file_content", content_type="image/jpeg")
#         }, format='multipart')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['status'], 'success')
#         self.profile.refresh_from_db()
#         self.assertEqual(self.profile.gender, 'F')
#         self.assertEqual(self.profile.viber, '380987654321')
#         self.assertTrue(self.profile.avatar.name.endswith('new_avatar.jpg'))

#     def test_profile_update_non_admin(self):
#         token = Token.objects.create(user=self.user)
#         self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
#         response = self.client.post('/api/profile/', {
#             'user': self.user.id + 1,
#             'gender': 'F'
#         }, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertIn('Ви не можете змінювати це поле', str(response.data))

#     def test_notification_settings(self):
#         token = Token.objects.create(user=self.user)
#         self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
#         response = self.client.get('/api/notifications/', format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(response.data['email_notifications'])

#         response = self.client.post('/api/notifications/', {
#             'email_notifications': False,
#             'sms_notifications': True
#         }, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['status'], 'success')
#         self.notifications.refresh_from_db()
#         self.assertFalse(self.notifications.email_notifications)
#         self.assertTrue(self.notifications.sms_notifications)

#     def test_logout(self):
#         token = Token.objects.create(user=self.user)
#         self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
#         response = self.client.post('/api/auth/logout/', {}, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['status'], 'success')
#         self.assertEqual(response.data['message'], 'Successfully logged out')
#         self.assertFalse(Token.objects.filter(user=self.user).exists())