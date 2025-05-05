from django.db import models
from django.contrib.auth.models import User
from product.models import SubProducts
from cart.models import Cart
from django.db.models import Sum
from product.utils import get_discounted_price
from warehouse.models import WarehouseStock, Warehouse
from discounts.models import BirthdayDiscount, Coupon
from decimal import Decimal
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _
class Order(TranslatableModel):
    STATUS_CHOICES = (
        ('new', _('New')),
        ('awaiting_payment', _('Awaiting Payment')),
        ('paid', _('Paid')),
        ('in_transit', _('In Transit')),  # Додаємо
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
        ('reversed', _('Reversed')),
        ('cancelled', _('Cancelled')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='orders')
    payment_method = models.CharField(max_length=20, choices=[('cash', _('Cash')), ('liqpay', 'LiqPay'), ('googlepay', 'GooglePay')], default='cash')
    delivery_method = models.CharField(max_length=20, choices=[('pickup', _('Pickup')), ('delivery', _('Delivery'))], default='pickup')
    recipient_name = models.CharField(max_length=100, blank=True, null=True)
    recipient_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    coupon = models.ForeignKey('discounts.Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    birthday_discount = models.ForeignKey('discounts.BirthdayDiscount', on_delete=models.SET_NULL, null=True, blank=True)
    call_me = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    final_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    status_pay = models.CharField(max_length=20, blank=True, null=True)
    tracking_number = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    def select_warehouse(self, product, quantity, address):
        """
        Вибирає склад для товару на основі адреси доставки.
        Повертає WarehouseStock і чи потрібно переміщення (in_transit).
        """
        # Спрощуємо: припускаємо, що address і location — це назви міст
        if not address:
            # Якщо адреса не вказана (наприклад, pickup), беремо перший склад із достатньою кількістю
            warehouses = Warehouse.objects.all()
        else:
            # Сортуємо склади за "відстанню" (спрощеним порівнянням міст)
            address_city = address.split(',')[0].strip().lower()  # Беремо першу частину адреси (місто)
            warehouses = sorted(
                Warehouse.objects.all(),
                key=lambda w: 0 if address_city in w.location.lower() else 1
            )

        # Шукаємо склад із достатньою кількістю товару
        for warehouse in warehouses:
            try:
                warehouse_stock = WarehouseStock.objects.get(warehouse=warehouse, product=product)
                if warehouse_stock.quantity >= quantity:
                    return warehouse_stock, False  # Товар є на складі, переміщення не потрібне
            except WarehouseStock.DoesNotExist:
                continue
        # Якщо товару немає, можна позначити як in_transit або кинути виняток
            print(f"No stock available for product {product.name}. Awaiting replenishment.")
            return None, True  # Повертаємо None і in_transit=True, щоб обробити пізніше
        # Якщо на найближчому складі не вистачає, шукаємо інший склад
        for warehouse in Warehouse.objects.all():
            try:
                warehouse_stock = WarehouseStock.objects.get(warehouse=warehouse, product=product)
                if warehouse_stock.quantity >= quantity:
                    print(f"Product {product.name} will be transferred from {warehouse.name} to {address}")
                    return warehouse_stock, True  # Товар є, але потрібно переміщення
            except WarehouseStock.DoesNotExist:
                continue

        raise ValueError(f"Not enough stock for product {product.name} on any warehouse")

    def _deduct_inventory(self):
        """Списуємо товари зі складів"""
        # Очищаємо попередні записи OrderStock
        self.stocks.all().delete()

        # Для кожного товару в замовленні вибираємо склад
        for item in self.items.all():
            subproduct = item.product
            product = subproduct.parent_product  # Отримуємо Product через зв’язок
            warehouse_stock, in_transit = self.select_warehouse(product, item.quantity, self.address)

            # Списуємо товар
            if warehouse_stock.quantity < item.quantity:
                raise ValueError(f"Insufficient stock for product {product.name} in warehouse {warehouse_stock.warehouse.name}")
            warehouse_stock.quantity -= item.quantity
            warehouse_stock.save()

            # Зберігаємо інформацію про склад
            OrderStock.objects.create(
                order=self,
                warehouse_stock=warehouse_stock,
                quantity=item.quantity,
                in_transit=in_transit
            )

        # Якщо є товари в дорозі, змінюємо статус
        if any(stock.in_transit for stock in self.stocks.all()):
            self.status = 'in_transit'
            self.save()

    def _mark_shipped(self):
        """Логіка відправлення"""
        if self.delivery_method == 'pickup':
            warehouses = {stock.warehouse_stock.warehouse.name for stock in self.stocks.all()}
            print(f"Order #{self.id} ready for pickup by {self.recipient_name} at {', '.join(warehouses)}")
        else:
            total_weight = sum(item.product.weight * item.quantity for item in self.items.all() if item.product.weight)
            in_transit = any(stock.in_transit for stock in self.stocks.all())
            if in_transit:
                print(f"Order #{self.id} is in transit and will be shipped to {self.address}, total weight: {total_weight} kg")
            else:
                print(f"Order #{self.id} has been shipped to {self.address}, total weight: {total_weight} kg")
            # Інтеграція з Nova Poshta
            # from novaposhta import NovaPoshta
            # np = NovaPoshta(api_key='your_api_key')
            # shipment = np.create_shipment(
            #     sender_city=self.stocks.first().warehouse_stock.warehouse.location,
            #     recipient_name=self.recipient_name,
            #     recipient_phone=self.recipient_phone,
            #     recipient_address=self.address,
            #     weight=total_weight
            # )
            # self.tracking_number = shipment.tracking_number
            self.save()
    def calculate_total(self):
        """Обчислює total_price і final_price з урахуванням знижок"""
        items = self.items.all()
        total_price = sum(item.total_price for item in items)
        discount = self.discount or Decimal('0.00')
        final_price = total_price * (1 - discount / 100)
        
        self.total_price = total_price
        self.final_price = round(final_price, 2)
        self.save()

    def __str__(self):
        return f'Order #{self.id} by {self.user or "Anonymous"}'

    def update_status(self, new_status, payment_status=None):
        """Метод для зміни статусу з логікою"""
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {new_status}")

        if new_status == 'awaiting_payment' and self.status == 'new':
            self.status = new_status
        elif new_status == 'paid' and self.status == 'awaiting_payment':
            if payment_status == 'success':
                self.status = new_status
                self.status_pay = payment_status
                self._deduct_inventory()
            else:
                self.status = 'failed'
                self.status_pay = payment_status
        elif new_status == 'failed' and self.status in ('new', 'awaiting_payment'):
            self.status = new_status
            self.status_pay = payment_status or 'failed'
        elif new_status == 'reversed' and self.status in ('awaiting_payment', 'paid'):
            self.status = new_status
            self.status_pay = payment_status or 'reversed'
        elif new_status == 'in_transit' and self.status == 'paid':
            self.status = new_status
        elif new_status == 'shipped' and self.status in ('paid', 'in_transit'):
            self.status = new_status
            self._mark_shipped()
        elif new_status == 'delivered' and self.status == 'shipped':
            self.status = new_status
        elif new_status == 'cancelled':
            self.status = new_status
        else:
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
        self.save()
# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='orders')
#     payment_method = models.CharField( max_length=20, choices=[('cash', 'Cash'), ('liqpay', 'LiqPay'), ('googlepay', 'GooglePay')], default='cash')
#     delivery_method = models.CharField( max_length=20,choices=[('pickup', 'Pickup'), ('delivery', 'Delivery')], default='pickup')
#     recipient_name = models.CharField(max_length=100, blank=True, null=True)
#     recipient_phone = models.CharField(max_length=20, blank=True, null=True)
#     address = models.TextField(blank=True, null=True)
#     coupon = models.ForeignKey('discounts.Coupon', on_delete=models.SET_NULL, null=True, blank=True)
#     birthday_discount = models.ForeignKey('discounts.BirthdayDiscount', on_delete=models.SET_NULL, null=True, blank=True)
#     call_me = models.BooleanField(default=False)
#     total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
#     discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
#     final_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
#     status = models.CharField( max_length=20, choices=[('new', 'New'), ('paid', 'Paid'), ('failed', 'Failed'), ('reversed', 'Reversed')], default='new')
#     status_pay = models.CharField(max_length=20, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = 'Order'
#         verbose_name_plural = 'Orders'

#     def calculate_total(self):
#         """Обчислює total_price і final_price з урахуванням знижок"""
#         items = self.items.all()
#         total_price = sum(item.total_price for item in items)
#         discount = self.discount or Decimal('0.00')
#         final_price = total_price * (1 - discount / 100)
        
#         self.total_price = total_price
#         self.final_price = round(final_price, 2)
#         self.save()

#     def __str__(self):
#         return f'Order #{self.id} by {self.user or "Anonymous"}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(SubProducts, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def save(self, *args, **kwargs):
        self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product} x {self.quantity} in Order #{self.order.id}'

# order/models.py
class OrderStock(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='stocks')
    warehouse_stock = models.ForeignKey('warehouse.WarehouseStock', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    in_transit = models.BooleanField(default=False)  # Позначаємо, якщо товар у дорозі

    class Meta:
        unique_together = ('order', 'warehouse_stock')

    def __str__(self):
        return f"{self.quantity} from {self.warehouse_stock.warehouse.name} for Order #{self.order.id}"