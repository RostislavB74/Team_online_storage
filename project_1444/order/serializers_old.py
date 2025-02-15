# def create(self, validated_data):
    #     order_items_data = validated_data.pop("order_items")
    #     order = Order.objects.create(**validated_data)

    #     for item_data in order_items_data:
    #         product_id = item_data["product"]  # Отримуємо ID продукту
    #         product = Product.objects.get(id=product_id)  # Завантажуємо продукт
    #         item_data["product"] = product  # Замінюємо ID на об'єкт
    #         item_data["price"] = product.price  # Додаємо ціну
    #         OrderItem.objects.create(order=order, **item_data)

    #     order.calculate_total_price()  # Оновлюємо загальну суму
    #     return order

# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True, write_only=True)
#     items_detail = OrderItemSerializer(source="order_items", many=True, read_only=True)
#     user = serializers.ReadOnlyField(source="user.username")

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "items_detail", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)
#         for item_data in order_items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         order.calculate_total_price()
#         return order
# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True)

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)

#         for item_data in order_items_data:
#             product = item_data["product"]  # Отримуємо продукт
#             price = product.price  # Беремо ціну товару
#             OrderItem.objects.create(order=order, price=price, **item_data)

#         order.calculate_total_price()  # Оновлюємо загальну ціну замовлення
#         return order


# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True)  
#     user = serializers.ReadOnlyField(source="user.username")

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)
#         for item_data in order_items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         order.calculate_total_price()
#         return order

# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True)  # Видалив read_only=True
#     user = serializers.ReadOnlyField(source="user.username")

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)
#         for item_data in order_items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         order.calculate_total_price()
#         return order

# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True)  # Видалив read_only=True
#     user = serializers.ReadOnlyField(source="user.username")

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)
#         for item_data in order_items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         order.calculate_total_price()
#         return order