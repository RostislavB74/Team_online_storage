# from django.shortcuts import render

# # Create your views here.
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .utils import get_user_available_discounts
# # from .serializers import AvailableDiscountSerializer

# class AvailableDiscountsView(APIView):
#     # serializer_class = AvailableDiscountSerializer
#     def get(self, request):

#         discounts = get_user_available_discounts(request.user)
#         data = [
#             {
#                 "id": d.id,
#                 "name": d.name,
#                 "percent": d.discount_percent,
#                 "valid_to": d.valid_to
#             }
#             for d in discounts
#         ]
#         return Response(data)
from django.db.models import F, FloatField
from django.db.models.functions import Abs
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Discount, PromoCode, Coupon, PersonalDiscount, BirthdayDiscount
from .serializers import (
    DiscountSerializer, PromoCodeSerializer, CouponSerializer,
    PersonalDiscountSerializer, BirthdayDiscountSerializer
)
from django.db import models  # Додаємо цей імпорт
from django.utils.timezone import now
from product.models import Product, Categories
from drf_spectacular.utils import extend_schema, OpenApiParameter
class AvailableDiscountsView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name="product_id", type=int, required=False),
            OpenApiParameter(name="category_id", type=int, required=False),
        ],
        responses={200: {"type": "object", "properties": {"discounts": {"type": "array"}}}}
    )
    
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        product_id = request.query_params.get("product_id")
        category_id = request.query_params.get("category_id")

        # Збираємо всі доступні знижки
        discounts = []

        # 1. Discount
        discount_qs = Discount.objects.filter(is_active=True, valid_from__lte=now(), valid_to__gte=now())
        if user:
            discount_qs = discount_qs.filter(profile__user=user) | discount_qs.filter(profile__isnull=True)
        if product_id:
            discount_qs = discount_qs.filter(products__id=product_id)
        if category_id:
            discount_qs = discount_qs.filter(categories__id=category_id)
        discounts.extend(
            DiscountSerializer(discount_qs.distinct(), many=True).data
        )

        # 2. PromoCode
        promo_qs = PromoCode.objects.filter(
            is_active=True, valid_from__lte=now(), valid_to__gte=now(), used_count__lt=models.F("usage_limit")
        )
        if product_id:
            promo_qs = promo_qs.filter(applicable_products__id=product_id)
        if category_id:
            promo_qs = promo_qs.filter(applicable_categories__id=category_id)
        discounts.extend(
            PromoCodeSerializer(promo_qs.distinct(), many=True).data
        )

        # 3. Coupon
        if user:
            coupon_qs = Coupon.objects.filter(
                profile__user=user, is_active=True, valid_from__lte=now(), valid_to__gte=now()
            )
            discounts.extend(
                CouponSerializer(coupon_qs.distinct(), many=True).data
            )

        # 4. PersonalDiscount
        if user:
            personal_qs = PersonalDiscount.objects.filter(
                profile__user=user, is_active=True, valid_from__lte=now(), valid_to__gte=now()
            )
            if product_id:
                personal_qs = personal_qs.filter(applicable_products__id=product_id)
            if category_id:
                personal_qs = personal_qs.filter(applicable_categories__id=category_id)
            discounts.extend(
                PersonalDiscountSerializer(personal_qs.distinct(), many=True).data
            )

        # 5. BirthdayDiscount
        if user and hasattr(user, 'profile'):
            birthday_qs = BirthdayDiscount.objects.filter(profile__user=user)
            birthday_qs = [bd for bd in birthday_qs if bd.is_valid]
            discounts.extend(
                BirthdayDiscountSerializer(birthday_qs, many=True).data
            )

        return Response({"discounts": discounts}, status=status.HTTP_200_OK)