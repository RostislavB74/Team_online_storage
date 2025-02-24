from rest_framework import serializers
from .models import Warehouse, WarehouseStock, Reservation

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class WarehouseStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseStock
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'


# class WarehouseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Warehouse
#         fields = '__all__'

# class WarehouseStockSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WarehouseStock
#         fields = '__all__'

# class ReservationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Reservation
#         fields = '__all__'