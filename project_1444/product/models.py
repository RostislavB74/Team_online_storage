import uuid
import qrcode
from datetime import datetime
from io import BytesIO
from django.db import models
from django.db.models.signals import pre_save
from django.core.files.base import ContentFile
from django.dispatch import receiver
from users.models import User
#Category items
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    class Meta:
        verbose_name = 'Категорія виробу'
        verbose_name_plural = 'Категорії виробів'
    def __str__(self):
        return f"{self.parent.name} -> {self.name}" if self.parent else self.name
#Material
class Material(models.Model):
    TYPE_CHOICES = [
        ('metal', 'Метал'),
        ('non-metal', 'Неметал'),
    ]
    
    PROBE_CHOICES = [
        ('0','0'),
        ('585', '585'),
        ('750', '750'),
        ('925', '925'),
        ('950', '950'),
    ]

    COLOR_CHOICES = [
        ('white', 'Білий'),
        ('yellow', 'Жовтий'),
        ('red', 'Червоний'),
        ('brown', 'Коричневий'),
        ('rhodium_plating', 'Родіювання'),
        ('black', 'Чорний'),
        ('blackening', 'Чорніння'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=255, blank=True, null=True)
    metal = models.CharField(max_length=50, choices=[('gold', 'Золото'), ('silver', 'Срібло'), ('platinum', 'Платина'), ('steel', 'Сталь'),])
    assay = models.CharField(max_length=20, choices=PROBE_CHOICES, null=True, blank=True)
    color = models.CharField(max_length=50, choices=COLOR_CHOICES, null=True, blank=True)
    article = models.CharField(max_length=20, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Матеріал'
        verbose_name_plural = 'Матеріали'

    def __str__(self):
        return f"{self.name} | {self.assay} | {self.color}"


# Функція для генерації артикула перед збереженням
@receiver(pre_save, sender=Material)
def generate_article(sender, instance, **kwargs):
    if not instance.article:
        metal_code = instance.metal[0].upper()  # G / S / P
        color_code = instance.color[0].upper() if instance.color else ''  # Y / W / R
        assay_code = str(instance.assay)  # 585, 925, 950

        last_material = Material.objects.order_by('-id').first()
        next_number = f"{(last_material.id + 1) if last_material else 1:03d}"  # 001, 002

        instance.article = f"{metal_code}{assay_code}{color_code}{next_number}"

#Gemstone
class Gemstone(models.Model):
    TYPE_CHOICES = [
        ('precious', 'Коштовний'),
        ('semi-precious', 'Напівкоштовний')
    ]
    ORIGIN_CHOICES = [
        ('natural', 'Природній'),
        ('synthetic', 'Синтетичний')
    ]
    LEVEL_CHOICES = [
        (1, '1st'),
        (2, '2nd'),
        (3, '3rd'),
        (4, '4th')
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    origin_stone = models.CharField(max_length=20, choices=ORIGIN_CHOICES)
    name = models.CharField(max_length=255)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    color = models.CharField(max_length=50, null=True, blank=True)
    class Meta:
        verbose_name = 'Ювеліриний камінь'
        verbose_name_plural = 'Ювелірне каміння'
    def __str__(self):
        return self.name
class Occasion(models.Model):
    name = models.CharField(max_length=255, unique=True)
    class Meta:
        verbose_name = 'Привід'
        verbose_name_plural = 'Приводи'
    def __str__(self):
        return self.name

class Gender(models.Model):
    GENDER_CHOICES = [
        ('female', 'Жіноче'),
        ('male', 'Чоловіче'),
        ('children', 'Дитяче'),
        ('unisex', 'Унісекс'),
    ]
    name = models.CharField(choices=GENDER_CHOICES, max_length=20)
    class Meta:
        ordering = ['name']
        verbose_name = 'Для кого'    
        verbose_name_plural = 'Для кого'
    def __str__(self):
        return self.name
#Product
class Product(models.Model):
    
    article = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Артикул
    ean_13 = models.CharField(max_length=13, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True) 
    name = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, blank=True)
    material = models.ForeignKey('Material', on_delete=models.SET_NULL, null=True, blank=True)
    size = models.CharField(max_length=10, null=True, blank=True)
    circumference_mm = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    weight_material = models.FloatField(null=True, blank=True)  # В грамах
    main_set_included = models.BooleanField(default=False)
    material_set = models.ForeignKey('Material', on_delete=models.SET_NULL, null=True, blank=True, related_name='products_with_material_set')
    gemstone_main = models.ForeignKey('Gemstone', on_delete=models.SET_NULL, null=True, blank=True, related_name='products_with_main_gem')
    description_gemstone_main = models.CharField(max_length=255, null=True, blank=True)
    color_gemstone_main = models.CharField(max_length=255, null=True, blank=True)
    weight_gemstone_main = models.FloatField(null=True, blank=True)
    set_included = models.BooleanField(default=False)
    gemstone_second = models.ForeignKey('Gemstone', on_delete=models.SET_NULL, null=True, blank=True, related_name='products_with_second_gem')
    description_gemstone_second = models.CharField(max_length=255, null=True, blank=True)
    weight_gemstone_second = models.FloatField(null=True, blank=True)
    dimensions = models.BooleanField(default=False) # Розміри
    width_mm = models.CharField(max_length=255, null=True, blank=True)
    length_mm = models.FloatField(null=True, blank=True)  # Розміри
    clasp_type = models.CharField(max_length=255, null=True, blank=True)
    coating = models.BooleanField(default=False)
    coating_material = models.CharField(max_length=255, null=True, blank=True)
    description_coating = models.CharField(max_length=255, null=True, blank=True)
    color_coating = models.CharField(max_length=255, null=True, blank=True)
    gold_plates = models.BooleanField(default=False)
    design_product = models.CharField(max_length=255, null=True, blank=True)
    style = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField('Gender', max_length=20, choices=Gender.GENDER_CHOICES, default='unisex', blank=True)
    occasions = models.ManyToManyField(Occasion, blank=True)
    collection = models.CharField(max_length=255, null=True, blank=True)
    year_collection = models.IntegerField(null=True, blank=True)  # Рік колекції, якщо є відповідне поле в формі
    country_of_origin = models.CharField(max_length=255, null=True, blank=True)
    description_product = models.TextField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)  # QR-код
    product_sertificate = models.ManyToManyField('ProductCertificate', related_name='product_certificates', blank=True)
    # created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        # Якщо вибрано основний камінь, встановлюємо його колір
        if self.gemstone_main:
            self.color_gemstone_main = self.gemstone_main.color  # Беремо колір каменю
            self.color_material = self.gemstone_main.color  # Призначаємо колір матеріалу
        else:
            self.color_gemstone_main = None
            self.color_material = None

        super().save(*args, **kwargs)  # Зберігаємо товар
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
    def get_material_info(self):
        return f"{self.material.article} | {self.material.name} | {self.material.metal} | {self.material.assay} | {self.material.color}" if self.material else "Матеріал не вибрано"


    def __str__(self):
        return f"{self.name} ({self.get_material_info()})"
    # def __str__(self):
    #     return self.name


# Функція для генерації `sku`
def generate_sku():
    return f"SKU-{uuid.uuid4().hex[:8].upper()}"


# Функція для генерації `article`
def generate_article(product):
    
# def generate_sku():
    last_product = Product.objects.order_by('-id').first()
    if last_product:
        # Припустимо, що перші два символи - це префікс
        last_article_number = int(last_product.article[2:])
        new_article = f"PR{last_article_number + 1:05d}"  # Формат: PR00001, PR00002, ...
    else:
        new_article = "PR00001"  # Початковий SKU
    return new_article
    

# Функція для генерації QR-коду
def generate_qr_code(product):
    """Генерує QR-код із `sku` або `ean_13`"""
    qr_data = product.sku or product.ean_13 or product.name
    qr = qrcode.make(qr_data)
    qr_io = BytesIO()
    qr.save(qr_io, format='PNG')
    qr_file = ContentFile(qr_io.getvalue(), name=f'qr_{product.sku}.png')
    return qr_file


# Сигнал `pre_save` для автоматичного заповнення SKU, артикулу та QR-коду
@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    if not instance.sku:
        instance.sku = generate_sku()
    if not instance.article:
        instance.article = generate_article(instance)
    if not instance.qr_code:
        instance.qr_code = generate_qr_code(instance)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Фото продукції'
        verbose_name_plural = 'Фото продукцій'
    def __str__(self):
        return f"{self.product.article} - Image"

class ProductCertificate(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='certificates')
    file = models.FileField(upload_to='product_certificates/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta: 
        verbose_name = 'Сертифікат продукції'
        verbose_name_plural = 'Сертифікати продукцій'
    def __str__(self):
        return f"{self.product.article} - Certificate"


class RingSizeConversion(models.Model):
    circumference_mm = models.FloatField(unique=True)  # Довжина кола
    diameter_mm = models.FloatField()  # Діаметр каблучки
    size_ua = models.CharField(max_length=10)  # Український розмір
    size_us = models.CharField(max_length=10,null=True, blank=True)  # США, Канада
    size_eu = models.CharField(max_length=10,null=True, blank=True)  # Європа
    size_uk = models.CharField(max_length=10,null=True, blank=True)  # Англія, Ірландія, Австралія
    size_asia = models.CharField(max_length=10, null=True, blank=True)  # Азія
    size_other_eu = models.CharField(max_length=10, null=True, blank=True)  # Решта Європи

    class Meta:
        verbose_name = 'Конвертація розмірів'
        verbose_name_plural = 'Конвертер розмірів'
    def __str__(self):
        return f"{self.circumference_mm} мм → {self.size_ua} (UA)"

def save(self, *args, **kwargs):
        if self.category and self.category.name.lower() == "каблучки" and self.circumference_mm:
            # Автоматично визначаємо розмір
            size_obj = RingSizeConversion.objects.filter(
                circumference_mm=self.circumference_mm
            ).first()
            if size_obj:
                self.size = size_obj.size_ua  # Вибираємо український розмір
        super().save(*args, **kwargs)