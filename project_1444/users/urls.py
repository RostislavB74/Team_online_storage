# from django.urls import path
# from .views import OTPRequestView, OTPVerifyView

# urlpatterns = [
#     path('send-otp/', OTPRequestView.as_view(), name='send-otp'),
#     path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from users.views import UserProfileView



# router = DefaultRouter()

# path("profile/", UserProfileView.as_view(), name="user-profile"),