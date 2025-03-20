import uuid
import qrcode
from io import BytesIO
from datetime import datetime
from django.db import models
from django.db.models.signals import pre_save
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from users.models import User
from parler.models import TranslatableModel, TranslatedFields
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .utils import save_with_translation
from cloudinary.models import CloudinaryField
from django.utils import translation
# Категорії
class Categories(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name='Categories'),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True), 
    )
    updated_at = models.DateTimeField(auto_now=True)
    has_length = models.BooleanField(default=False, verbose_name="Має довжину (см)")
    has_width = models.BooleanField(default=False, verbose_name="Має ширину (см)")
    has_diameter = models.BooleanField(default=False, verbose_name="Має діаметр (мм)")
    has_weight = models.BooleanField(default=True, verbose_name="Має вагу (г)")
    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = 'Категорія виробу'
        verbose_name_plural = 'Категорії виробів'

    def __str__(self):
        return self.safe_translation_getter('name', default='Без назви')  # Бере name із перекладу


class SubCategories(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )
    parent = models.ForeignKey(Categories, on_delete=models.PROTECT, null=True, blank=True, related_name='subcategories')
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = 'Підкатегорія виробу'
        verbose_name_plural = 'Підкатегорії виробів'

    def __str__(self):
        return self.safe_translation_getter('name', default='Без назви')  

class Colors(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name='Colors'),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True), 
    )

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = 'Колір'
        verbose_name_plural = 'Кольори'

    def __str__(self):
        return self.safe_translation_getter('name', default='Без назви')  # Бере name із перекладу 
class Collections(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name='Collections'),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True), 
    )

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = 'Колекція'
        verbose_name_plural = 'Колекції'

    def __str__(self):
        return self.safe_translation_getter('name', default='Без назви')  # Бере name із перекладу
# Матеріали
class Material(TranslatableModel):

    PROBE_CHOICES = [
        ('0', '0'),
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
    METAL_CHOICES = [
        ('gold', 'Золото'), 
        ('silver', 'Срібло'), 
        ('platinum', 'Платина'), 
        ('steel', 'Сталь'),

    ]
    material = models.CharField(max_length=50,choices=METAL_CHOICES,null=True, blank=True)
    assay = models.CharField(max_length=20, choices=PROBE_CHOICES, null=True, blank=True)
    color = models.CharField(max_length=50, choices=COLOR_CHOICES, null=True, blank=True)
    article = models.CharField(max_length=20, unique=True, blank=True, null=True)
    translations = TranslatedFields(
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),    
    )
    
    
    class Meta:
        verbose_name = 'Матеріал'
        verbose_name_plural = 'Матеріали'

    def __str__(self):
        return f"{self.material} | {self.assay} | {self.color}"

# Функція для генерації артикула перед збереженням
@receiver(pre_save, sender=Material)
def generate_article(sender, instance, **kwargs):
    if not instance.article:
        metal_code = instance.material[0].upper() if instance.material else ''  # Перевірка, чи є metal
        color_code = instance.color[0].upper() if instance.color else ''  # Перевірка, чи є color
        assay_code = str(instance.assay) if instance.assay else ''  # Перевірка, чи є assay
        last_material = Material.objects.order_by('-id').first()
        next_number = f"{(last_material.id + 1) if last_material else 1:03d}"  # Генерація номера
        instance.article = f"{metal_code}{assay_code}{color_code}{next_number}"

#Gemstone
class TypeGemstones(models.TextChoices):
    PRECIOUS = "precious", _("Precious")
    SEMIPRECIOUS = "semi-precious", _("Semi-Precious")
    NONPRECIOUS = "nonprecious", _("NonPrecious")

class Origin(models.TextChoices):
    NATURAL = "natural", _("Natural")
    SYNTHETIC = "synthetic", _("Synthetic")

class OrderLevel(models.TextChoices):
    PRECIOUS_I = "precious_1", _("Precious I Order")      
    PRECIOUS_II = "precious_2", _("Precious II Order")    
    PRECIOUS_III = "precious_3", _("Precious III Order")  
    PRECIOUS_IV = "precious_4", _("Precious IV Order")    

    SEMI_PRECIOUS_I = "semi_precious_1", _("Semi-Precious I Order")  
    SEMI_PRECIOUS_II = "semi_precious_2", _("Semi-Precious II Order") 

class Gemstone(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug = models.SlugField(unique=True),
   )
    
    type = models.CharField(max_length=20, choices=TypeGemstones.choices, null=True, blank=True)
    origin_stone = models.CharField(max_length=20, choices=Origin.choices,  null=True, blank=True)
    level = models.CharField(max_length=20, choices=OrderLevel.choices, null=True, blank=True )
    # color = models.ForeignKey('Colors', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Ювелірний камінь'
        verbose_name_plural = 'Ювелірне каміння'

    def __str__(self):
        return self.safe_translation_getter('name', default='Без назви')

    def clean(self):
        """ Валідація категорій каменів """
        if self.origin_stone == Origin.SYNTHETIC and self.level:
            raise ValidationError({'level': _('Синтетичні камені не мають порядку.')})

        if self.type == TypeGemstones.PRECIOUS and self.level not in [
            OrderLevel.PRECIOUS_I, OrderLevel.PRECIOUS_II,
            OrderLevel.PRECIOUS_III, OrderLevel.PRECIOUS_IV
        ]:
            raise ValidationError({'level': _('Дорогоцінні камені мають рівні I-IV порядку.')})

        if self.type == TypeGemstones.SEMIPRECIOUS and self.level not in [
            OrderLevel.SEMI_PRECIOUS_I, OrderLevel.SEMI_PRECIOUS_II
        ]:
            raise ValidationError({'level': _('Напівкоштовні камені мають рівні I-II порядку.')})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Occasion(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True),
        slug=models.SlugField(max_length=50, unique=True, blank=True),
    )

    class Meta:
        verbose_name = "Привід"
        verbose_name_plural = "Приводи"
    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)
    def __str__(self):
        return self.safe_translation_getter('name', default='Без назви')  # Бере name із перекладу



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

class SubProducts(models.Model):
    parent_product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="products", verbose_name=_("Продукт"))
    position = models.IntegerField(null=True, blank=True)
    article = models.CharField(max_length=50, unique=True, blank=True, null=True)
    ean_13 = models.CharField(max_length=13, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True) 
    price = models.FloatField(null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])  
    new_price = models.FloatField(null=True, blank=True)
    old_price = models.FloatField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    length = models.FloatField(null=True, blank=True, verbose_name="Довжина (см)")
    width = models.FloatField(null=True, blank=True, verbose_name="Ширина (см)")
    size = models.FloatField(null=True, blank=True, verbose_name="Розмір(мм) ")
    weight = models.FloatField(null=True, blank=True, verbose_name="Вага (г)")
    def clean(self):
        if self.parent_product and self.parent_product.category:
            self.category = self.parent_product.category

        """Перед збереженням перевіряємо, які поля потрібні"""
        if not self.category.has_length:
            self.length = None
        if not self.category.has_width:
            self.width = None
        if not self.category.has_diameter:
            self.diameter = None
        if not self.category.has_weight:
            self.weight = None

    def save(self, *args, **kwargs):
        """Автоматично встановлює порядковий номер для кожного продукту."""
        if not self.pk:  # Якщо створюється новий запис
            last_subproduct = SubProducts.objects.filter(parent_product=self.parent_product).order_by("position").last()
            self.position = (last_subproduct.position + 1) if last_subproduct else 1

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.parent_product} - {self.length or ''}x{self.width or ''}x{self.size or ''} мм, {self.weight} г"
def generate_subarticle(product):
    last_product = SubProducts.objects.order_by('-id').first()
    if last_product:
        # Припустимо, що перші два символи - це префікс
        last_article_number = int(last_product.article[4:])
        new_article = f"SBPR{last_article_number + 1:05d}"  # Формат: PR00001, PR00002, ...
    else:
        new_article = "SBPR00001"  # Початковий SKU
    return new_article
    
@receiver(pre_save, sender=SubProducts)
def subproduct_pre_save(sender, instance, **kwargs):
    if not instance.sku:
        instance.sku = generate_sku()
    if not instance.article:
        instance.article = generate_subarticle(instance)
    if not instance.qr_code:
        instance.qr_code = generate_qr_code(instance)


class ProductAttributes(TranslatableModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="attributes")
    gender = models.CharField('Gender', max_length=20, choices=Gender.GENDER_CHOICES, default='unisex', blank=True)
    color_coating=models.ForeignKey('Colors', on_delete=models.SET_NULL, null=True, blank=True)
    statuses = models.ManyToManyField('ProductStatus', blank=True, related_name="products")
    translations = TranslatedFields(
        clasp_type = models.CharField(max_length=255, blank=True, null=True),
        coating_material = models.CharField(max_length=255, blank=True, null=True),
        description_coating = models.CharField(max_length=255, blank=True, null=True),
        design_product = models.CharField(max_length=255, blank=True, null=True),
        style = models.CharField(max_length=255, blank=True, null=True),
    )
   
class ProductStatus(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True), 
    )
    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)
    


class ProductMaterial(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='materials')
    material = models.ForeignKey('Material', on_delete=models.SET_NULL, null=True, blank=True)
    is_primary = models.BooleanField(default=False)  # Чи основний матеріал
    set_included = models.BooleanField(default=False) 
    
    class Meta:
        unique_together = ('product', 'material')  # Уникнення дублювань

    def __str__(self):
        return f"{self.product} - {self.material}"


class ProductGemstone(TranslatableModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="gemstones")
    gemstone = models.ForeignKey('Gemstone', on_delete=models.CASCADE)
    color = models.ForeignKey('Colors', on_delete=models.SET_NULL, null=True, blank=True)  # Колір каменю
    weight = models.FloatField(null=True, blank=True)  # Вага каменю
    is_main = models.BooleanField(default=False)  # Основний камінь
    set_included = models.BooleanField(default=False)  # Камінь в комплекті

    translations = TranslatedFields(
        description = models.CharField(max_length=255, blank=True, null=True),
    )

    class Meta:
        unique_together = ('product', 'gemstone', 'color')  # Один і той самий камінь може бути різного кольору

    def clean(self):
        """ Забезпечуємо, що тільки один камінь у виробі є основним. """
        if self.is_main:
            existing_main = ProductGemstone.objects.filter(product=self.product, is_main=True).exclude(pk=self.pk)
            if existing_main.exists():
                raise ValidationError("У виробі вже є основний камінь!")

    def save(self, *args, **kwargs):
        self.clean()  # Викликаємо перевірку перед збереженням
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} - {self.gemstone} ({self.color}, {self.weight}g, {'Основний' if self.is_main else 'Додатковий'})"

class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField("image")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Фото продукції'
        verbose_name_plural = 'Фото продукцій'
    def __str__(self):
        return f"{self.product.article} - Image"

class ProductCertificate(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='certificates')
    file = models.FileField(upload_to='product_certificates/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta: 
        verbose_name = 'Сертифікат продукції'
        verbose_name_plural = 'Сертифікати продукцій'
    def __str__(self):
        return f"{self.product.article} - Certificate"

class Product(TranslatableModel):
    
    category = models.ForeignKey('Categories', on_delete=models.SET_NULL, null=True, blank=True)
    subproducts = models.ManyToManyField("SubProducts", related_name="subproducts", blank=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, null=True, blank=True),
        description_product=models.TextField(null=True, blank=True),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )
    category = models.ForeignKey('Categories', on_delete=models.SET_NULL, null=True, blank=True)
    subcategory=models.ForeignKey('SubCategories', on_delete=models.SET_NULL, null=True, blank=True)
    collection = models.ForeignKey('Collections', on_delete=models.SET_NULL, null=True, blank=True)
    occasions = models.ManyToManyField('Occasion', blank=True)
    article = models.CharField(max_length=50, unique=True, blank=True, null=True)
    ean_13 = models.CharField(max_length=13, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True) 
    year_collection = models.IntegerField(null=True, blank=True)
    country_of_origin = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

   
    def __str__(self):
        translation = self.safe_translation_getter('name', any_language=True)
        return translation if translation else f"Product {self.id}"





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