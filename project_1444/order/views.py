from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({"status": "updated", "new_status": order.get_status_display()})
        return Response({"error": "Invalid status"}, status=400)

# from django.shortcuts import render
# from rest_framework import viewsets, permissions
# from .models import Order, OrderItem
# from .serializers import OrderSerializer, OrderItemSerializer
# from rest_framework.decorators import action
# from rest_framework.response import Response

# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all().order_by("-created_at")
#     serializer_class = OrderSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         print(self.request.data)  # Подивись, що приходить
#         serializer.save(user=self.request.user)
   
#     @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
#     def update_status(self, request, pk=None):
#         order = self.get_object()
#         new_status = request.data.get("status")
#         if new_status in dict(Order.STATUS_CHOICES):
#             order.status = new_status
#             order.save()
#             return Response({"status": "updated", "new_status": order.get_status_display()})
#         return Response({"error": "Invalid status"}, status=400)