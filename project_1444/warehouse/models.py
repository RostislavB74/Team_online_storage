from django.db import models
from product.models import Product
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action


User = get_user_model()


class Warehouse(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Склад")
        verbose_name_plural = _("Склади")

    def __str__(self):
        return self.name


class WarehouseStock(models.Model):
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="stock"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="warehouses"
    )
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("warehouse", "product")

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.quantity}"

    def reserve_product(self, user, quantity, duration_minutes=30):
        if self.quantity < quantity:
            raise ValueError(_("Not enough stock available"))

        expires_at = now() + timedelta(minutes=duration_minutes)
        reservation = Reservation.objects.create(
            user=user,
            product=self.product,
            warehouse=self.warehouse,
            quantity=quantity,
            expires_at=expires_at,
        )
        self.quantity -= quantity
        self.save()
        return reservation

    def release_reservation(self, reservation):
        self.quantity += reservation.quantity
        reservation.delete()
        self.save()


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reservations"
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="reservations"
    )
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ("product", "warehouse", "user")

    def __str__(self):
        return "Reservation: {} - {} pcs at {}".format(
            self.product.name, self.quantity, self.warehouse.name
        )

    def is_expired(self):
        return now() > self.expires_at

    def cancel_reservation(self):
        if self.is_expired():
            warehouse_stock = self.warehouse.stock.get(product=self.product)
            warehouse_stock.release_reservation(self)


# Serializers
