# class Product(models.Model):
#     article = models.CharField(max_length=50, unique=True, blank=True, null=True) 
#     name = models.CharField(max_length=255)
#     category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
#     material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
#     metal_standard = models.ForeignKey(MetalStandard, on_delete=models.SET_NULL, null=True, blank=True)
#     gemstone = models.ForeignKey(Gemstone, on_delete=models.SET_NULL, null=True, blank=True)
#     gem_category = models.ForeignKey(GemCategory, on_delete=models.SET_NULL, null=True, blank=True)
#     weight = models.FloatField(null=True, blank=True)
#     dimensions = models.CharField(max_length=255, null=True, blank=True)  # Розміри
#     size = models.CharField(max_length=50, null=True, blank=True)  # Для кілець
#     purchase_reason = models.CharField(max_length=255, null=True, blank=True)
#     clasp_type = models.CharField(max_length=255, null=True, blank=True)
#     style = models.CharField(max_length=255, null=True, blank=True)
#     weaving_type = models.CharField(max_length=255, null=True, blank=True)
#     coating = models.BooleanField(default=False)
#     coating_material = models.CharField(max_length=255, null=True, blank=True)
#     gold_plates = models.BooleanField(default=False)
#     collection = models.CharField(max_length=255, null=True, blank=True)
#     set_included = models.BooleanField(default=False)
#     country_of_origin = models.CharField(max_length=255, null=True, blank=True)
#     created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     ean_13 = models.CharField(max_length=13, null=True, blank=True)
#     qr_code = models.CharField(max_length=255, null=True, blank=True)
#     sku = models.CharField(max_length=255, unique=True)
#     # Фото товару (декілька)
#     images = models.ManyToManyField('ProductImage', related_name='product_images', blank=True)
#     # Сертифікати (декілька)
#     certificates = models.ManyToManyField('ProductCertificate', related_name='product_certificates',  blank=True)
#     class Meta:
#         verbose_name = 'Товар'
#         verbose_name_plural = 'Товари'
#     def save(self, *args, **kwargs):
#         if not self.sku:
#             self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"  # Генеруємо `sku`, якщо його немає
#         if not self.article:
#             self.article = self.generate_article()  # Генеруємо `article`
#         super().save(*args, **kwargs)

#     def generate_article(self):
#         """Генеруємо артикул на основі SKU"""
#         if self.sku:
#             return f"ART-{self.sku.split('-')[-1]}"  # Наприклад, ART-1A2B3C4D
#         return None

#     def __str__(self):
#         return self.name
# @receiver(pre_save, sender=Product)
# def generate_article(sender, instance, **kwargs):
#     """Генерує артикул перед збереженням товару"""
#     if not instance.article:  # Генеруємо артикул тільки якщо він ще не заданий
#         parts = []

#         # Використовуємо перші цифри SKU як номер дизайну (або інший унікальний номер)
#         if instance.sku:
#             parts.append(instance.sku.split('-')[0])  # Беремо першу частину SKU (до "-")

#         # Додаємо першу літеру металу (наприклад, "Б" для білого золота)
#         if instance.metal_standard:
#             metal_code = instance.metal_standard.material.name[0].lower()
#             parts.append(metal_code)

#         # Якщо є покриття (емаль), додаємо "е"
#         if instance.coating:
#             parts.append('e')

#         instance.article = ''.join(parts)  # Формуємо рядок без пробілів
# @receiver(pre_save, sender=Product)
# def generate_sku(sender, instance, **kwargs):
#     """Генерує унікальний SKU перед збереженням товару"""
#     if not instance.sku:
#         instance.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"

# @receiver(pre_save, sender=Product)
# def generate_sku(sender, instance, **kwargs):
#     if not instance.sku:
#         instance.sku = f"{instance.category.name[:3].upper()}-{instance.material.name[:3].upper()}-{instance.pk}"

# @receiver(pre_save, sender=Product)
# def generate_sku():
#     last_product = Product.objects.order_by('-id').first()
#     if last_product:
#         # Припустимо, що перші два символи - це префікс
#         last_sku_number = int(last_product.sku[2:])
#         new_sku = f"PR{last_sku_number + 1:05d}"  # Формат: PR00001, PR00002, ...
#     else:
#         new_sku = "PR00001"  # Початковий SKU
#     return new_sku

# """Генерує артикул: [код матеріалу]-[колір металу]-[код вставки]"""
    # material_code = product.material.name if product.material else 'XX'
    # # color_code = product.coating_material.color if product.metal.color else 'X'
    # stone_code = product.gemstone.name if product.gemstone else '00'
    # return f"{material_code}-{stone_code}-{uuid.uuid4().hex[:8].upper()}"
# class ProductImage(models.Model):
#     product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="images")
#     image = models.ImageField(upload_to="products/images/")
#     is_main = models.BooleanField(default=False)  # Головне фото товару
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Image for {self.product.name}"
    
# class ProductCertificate(models.Model):
#     product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="certificates")
#     file = models.FileField(upload_to="products/certificates/")
#     description = models.CharField(max_length=255, blank=True, null=True)
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Certificate for {self.product.name}"

