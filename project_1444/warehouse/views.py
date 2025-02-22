from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Warehouse, WarehouseStock, Reservation
from .serializers import WarehouseSerializer, WarehouseStockSerializer, ReservationSerializer

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]

class WarehouseStockViewSet(viewsets.ModelViewSet):
    queryset = WarehouseStock.objects.all()
    serializer_class = WarehouseStockSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        stock = self.get_object()
        quantity = int(request.data.get('quantity', 0))
        if quantity <= 0:
            return Response({"error": "Invalid quantity"}, status=400)
        try:
            reservation = stock.reserve_product(request.user, quantity)
            return Response(ReservationSerializer(reservation).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        reservation.cancel_reservation()
        return Response({"message": "Reservation cancelled"})


# Create your views here.
# ViewSets
# class WarehouseViewSet(viewsets.ModelViewSet):
#     queryset = Warehouse.objects.all()
#     serializer_class = WarehouseSerializer
#     permission_classes = [permissions.IsAuthenticated]

# class WarehouseStockViewSet(viewsets.ModelViewSet):
#     queryset = WarehouseStock.objects.all()
#     serializer_class = WarehouseStockSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     @action(detail=True, methods=['post'])
#     def reserve(self, request, pk=None):
#         stock = self.get_object()
#         quantity = int(request.data.get('quantity', 0))
#         if quantity <= 0:
#             return Response({"error": "Invalid quantity"}, status=400)
#         try:
#             reservation = stock.reserve_product(request.user, quantity)
#             return Response(ReservationSerializer(reservation).data)
#         except ValueError as e:
#             return Response({"error": str(e)}, status=400)

# class ReservationViewSet(viewsets.ModelViewSet):
#     queryset = Reservation.objects.all()
#     serializer_class = ReservationSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     @action(detail=True, methods=['post'])
#     def cancel(self, request, pk=None):
#         reservation = self.get_object()
#         reservation.cancel_reservation()
#         return Response({"message": "Reservation cancelled"})
