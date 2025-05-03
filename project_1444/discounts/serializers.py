from rest_framework import serializers
from .models import (
    Discount, PromoCode, Coupon, PersonalDiscount, BirthdayDiscount,
    Product, Categories, Occasion, Material, Gemstone, RingSizeConversion,
    Gender, Collections, Styles, UserProfile
)
from product.serializers import ProductSerializer, CategoriesSerializer
from users.serializers import UserProfileSerializer
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now
class DiscountSerializer(serializers.ModelSerializer):
    discount_type = serializers.ChoiceField(choices=Discount.DiscountType.choices)
    products = ProductSerializer(many=True, read_only=True)
    categories = CategoriesSerializer(many=True, read_only=True)
    occasions = serializers.StringRelatedField(many=True, read_only=True)
    materials = serializers.StringRelatedField(many=True, read_only=True)
    gemstones = serializers.StringRelatedField(many=True, read_only=True)
    sizes = serializers.StringRelatedField(many=True, read_only=True)
    genders = serializers.StringRelatedField(many=True, read_only=True)
    collections = serializers.StringRelatedField(many=True, read_only=True)
    styles = serializers.StringRelatedField(many=True, read_only=True)
    profile = UserProfileSerializer(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Discount
        fields = [
            "id", "name", "discount_type", "discount_percent", "valid_from", "valid_to",
            "is_active", "combine_with_others", "priority", "profile", "products",
            "categories", "occasions", "materials", "gemstones", "sizes", "genders",
            "collections", "styles", "is_valid"
        ]

class PromoCodeSerializer(serializers.ModelSerializer):
    applicable_products = ProductSerializer(many=True, read_only=True)
    applicable_categories = CategoriesSerializer(many=True, read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = PromoCode
        fields = [
            "id", "code", "discount_percentage", "valid_from", "valid_to",
            "is_active", "combine_with_others", "usage_limit", "used_count",
            "applicable_products", "applicable_categories", "created_at", "is_valid"
        ]

class CouponSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    email = serializers.CharField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            "id", "profile", "discount_percentage", "valid_from", "valid_to",
            "is_active", "combine_with_others", "created_at", "is_valid", "email"
        ]

class PersonalDiscountSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    assigned_by = serializers.StringRelatedField(read_only=True)
    applicable_products = ProductSerializer(many=True, read_only=True)
    applicable_categories = CategoriesSerializer(many=True, read_only=True)
    user_groups = serializers.StringRelatedField(many=True, read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    email = serializers.CharField(read_only=True)

    class Meta:
        model = PersonalDiscount
        fields = [
            "id", "profile", "assigned_by", "discount_percentage", "valid_from",
            "valid_to", "is_active", "combine_with_others", "applicable_products",
            "applicable_categories", "user_groups", "created_at", "is_valid", "email"
        ]

# class BirthdayDiscountSerializer(serializers.ModelSerializer):
#     profile = UserProfileSerializer(read_only=True)
#     is_valid = serializers.BooleanField(read_only=True)
#     email = serializers.CharField(read_only=True)

#     class Meta:
#         model = BirthdayDiscount
#         fields = [
#             "id", "profile", "discount_percentage", "valid_days", "created_at",
#             "is_valid", "email"
#         ]
class BirthdayDiscountSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    email = serializers.CharField(read_only=True)
    code = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    valid_until = serializers.SerializerMethodField()

    class Meta:
        model = BirthdayDiscount
        fields = [
            "id", "profile", "discount_percentage", "valid_days", "created_at",
            "is_valid", "email", "code", "description", "discount", "valid_until"
        ]

    def get_code(self, obj):
        return f"BIRTHDAY{obj.discount_percentage}"

    def get_description(self, obj):
        return f"{obj.discount_percentage}% off for your birthday"

    def get_discount(self, obj):
        return float(obj.discount_percentage)

    def get_valid_until(self, obj):
        if obj.birthday_at_creation:
            return obj.birthday_at_creation.replace(year=now().year) + timedelta(days=obj.valid_days)
        return None

class ApplyDiscountResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["success", "error"])
    message = serializers.CharField()
    discount = serializers.FloatField(required=False)