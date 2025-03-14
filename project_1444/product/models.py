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

from .utils import save_with_translation
from cloudinary.models import CloudinaryField
# Категорії
class Categories(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name='Categories'),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True), 
    )
    updated_at = models.DateTimeField(auto_now=True)
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

class ProductStatus(models.TextChoices):
    BESTSELLER = "bestseller", _("Bestseller")
    NEW = "new", _("New")
    CLASSIC = "classic", _("Classic")
    STOCK = "stock", _("Stock")

#Gemstone
class TypeGemstones(models.TextChoices):
    """Тип каменів: коштовні та напівкоштовні"""
    PRECIOUS = "precious", _("Precious")
    SEMIPRECIOUS = "semi-precious", _("Semi-Precious")

class Origin(models.TextChoices):
    """Походження каменю"""
    NATURAL = "natural", _("Natural")
    SYNTHETIC = "synthetic", _("Synthetic")

class Gemstone(TranslatableModel):
    """Модель для зберігання каменів"""

    LEVEL_CHOICES = [
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
    ]

    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=20, choices=TypeGemstones.choices)
    origin = models.CharField(max_length=20, choices=Origin.choices, null=True, blank=True)
    level = models.IntegerField(choices=LEVEL_CHOICES, null=True, blank=True)
    color = models.ForeignKey('Colors', on_delete=models.SET_NULL, null=True, blank=True)

    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )

    class Meta:
        verbose_name = _("Ювелірне каміння")
        verbose_name_plural = _("Ювелірне каміння")

    def save(self, *args, **kwargs):
        """Перевіряє рівень залежно від типу каменю"""
        if self.type == TypeGemstones.PRECIOUS and self.level not in [1, 2, 3, 4]:
            raise ValueError(_("Precious gemstones must have a level from 1 to 4."))
        elif self.type == TypeGemstones.SEMIPRECIOUS and self.level not in [1, 2]:
            raise ValueError(_("Semi-precious gemstones must have a level of 1 or 2."))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter("name", default=_("Unnamed"))


class GemstoneCertificate(models.Model):
    """Зберігає сертифікати (наприклад, GIA)"""

    class CertificateType(models.TextChoices):
        GIA = "GIA", _("GIA")
        IGI = "IGI", _("IGI")
        HRD = "HRD", _("HRD")

    gemstone = models.OneToOneField(Gemstone, on_delete=models.CASCADE, related_name="certificate")
    certificate_type = models.CharField(max_length=10, choices=CertificateType.choices)
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateField()
    file = models.FileField(upload_to="certificates/", null=True, blank=True)

    class Meta:
        verbose_name = _("Gemstone Certificate")
        verbose_name_plural = _("Gemstone Certificates")

    def __str__(self):
        return f"{self.get_certificate_type_display()} - {self.certificate_number}"
# class TypeGemstones(models.TextChoices):
#     PRECICIOUS = "precious", _("Precious")
#     SEMIPRECIOUS = "semi-precious", _("Semi-Precious")

# class Origin(models.TextChoices):
#     NATURAL = "natural", _("Natural")
#     SYNTHETIC = "synthetic", _("Synthetic")
# class Gemstone(TranslatableModel):
   
#     LEVEL_CHOICES = [
#         (1, '1st'),
#         (2, '2nd'),
#         (3, '3rd'),
#         (4, '4th')
#     ]
    
#     type = models.ForeignKey('TypeGemstones', on_delete=models.SET_NULL, null=True, blank=True)
#     origin_stone = models.ForeignKey('Origin', on_delete=models.SET_NULL, null=True, blank=True)
#     level = models.IntegerField(choices=LEVEL_CHOICES, null=True, blank=True)
#     color=models.ForeignKey('Colors', on_delete=models.SET_NULL, null=True, blank=True)
#     translations = TranslatedFields(
#         name = models.CharField(max_length=255),
#         slug=models.SlugField(max_length=255, unique=True, blank=True, null=True), 
#     )
#     def save(self, *args, **kwargs):
#         save_with_translation(self, *args, **kwargs)
#     class Meta:
#         verbose_name = 'Ювеліриний камінь'
#         verbose_name_plural = 'Ювелірне каміння'
#     def __str__(self):
#         return self.safe_translation_getter('name', default='Без назви')  
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
class ProductAttributes(TranslatableModel):
    product = models.OneToOneField('Product', on_delete=models.CASCADE, related_name="attributes")
    gender = models.CharField('Gender', max_length=20, choices=Gender.GENDER_CHOICES, default='unisex', blank=True)
    color_coating=models.ForeignKey('Colors', on_delete=models.SET_NULL, null=True, blank=True)
    
    translations = TranslatedFields(
        clasp_type = models.CharField(max_length=255, blank=True, null=True),
        coating_material = models.CharField(max_length=255, blank=True, null=True),
        description_coating = models.CharField(max_length=255, blank=True, null=True),
        design_product = models.CharField(max_length=255, blank=True, null=True),
        style = models.CharField(max_length=255, blank=True, null=True),
        status = models.CharField(max_length=20, choices=ProductStatus.choices, default=ProductStatus.CLASSIC),
    )
    # def save(self, *args, **kwargs):
    #     save_with_translation(self, *args, **kwargs)

class ProductTag(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True), 
    )
    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)
    


class ProductMaterial(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="materials")
    is_primary = models.BooleanField(default=False)  # Чи основний матеріал
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('product', 'material')  # Уникнення дублювань

    # def save(self, *args, **kwargs):
    #     save_with_translation(self, *args, **kwargs)
    

class ProductGemstone(TranslatableModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="gemstones")
    gemstone = models.ForeignKey('Gemstone', on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)  # Основний камінь
    color=models.ForeignKey('Colors', on_delete=models.SET_NULL, null=True, blank=True)
    weight_gemstone_main = models.FloatField(null=True, blank=True)
    set_included = models.BooleanField(default=False)
    weight_gemstone_second = models.FloatField(null=True, blank=True)
    translations = TranslatedFields(
        gemstone_first = models.ForeignKey('Gemstone', on_delete=models.SET_NULL, null=True, blank=True, related_name='products_with_gem'),
        description_gemstone_first = models.CharField(max_length=255, null=True, blank=True),
        gemstone_second = models.ForeignKey('Gemstone', on_delete=models.SET_NULL, null=True, blank=True, related_name='products_with_second_gem'),
        description_gemstone_second = models.CharField(max_length=255, null=True, blank=True),
        description=models.CharField(max_length=255, blank=True, null=True),
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Спочатку зберігаємо, щоб отримати ID

        if self.is_main and self.gemstone:
            for lang in self.gemstone.get_available_languages():
                with self.translate(lang):
                    self.color = self.gemstone.safe_translation_getter('color', default="", language_code=lang)
            super().save(update_fields=["color"])  # Оновлюємо тільки поле color

    class Meta:
        unique_together = ('product', 'gemstone')



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
    subcategory=models.ForeignKey('SubCategories', on_delete=models.SET_NULL, null=True, blank=True)
    collection=models.ForeignKey('Collections', on_delete=models.SET_NULL, null=True, blank=True)
    occasions = models.ManyToManyField('Occasion', blank=True)
    translations = TranslatedFields(
        name = models.CharField(max_length=255,unique=True, null=True, blank=True),
        description_product = models.TextField(null=True, blank=True),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True), 
    )
    article = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Артикул
    ean_13 = models.CharField(max_length=13, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True) 
    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)
    size = models.CharField(max_length=10, null=True, blank=True)
    circumference_mm = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])  
    new_price = models.FloatField(null=True, blank=True)
    old_price = models.FloatField(null=True, blank=True)
    weight_material = models.FloatField(null=True, blank=True)  # В грамах
    main_set_included = models.BooleanField(default=False)
    
    dimensions = models.BooleanField(default=False) # Розміри
    width_mm = models.CharField(max_length=255, null=True, blank=True)
    length_mm = models.FloatField(null=True, blank=True)  # Розміри
    coating = models.BooleanField(default=False)
    gold_plates = models.BooleanField(default=False)
    year_collection = models.IntegerField(null=True, blank=True)  # Рік колекції, якщо є відповідне поле в формі
    country_of_origin = models.CharField(max_length=255, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)  # QR-код
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_occasion_name(self, lang='uk'):
        occasion_names = [occasion.translations.filter(language=lang).first().name if occasion.translations.filter(language=lang).first() else "Без назви" for occasion in self.occasions.all()]
        return ", ".join(occasion_names) if occasion_names else "Без назви"
    
    def discounted_price(self):
        if self.discount_percentage:
            discount_amount = self.price * (self.discount_percentage / 100)
            new_price = self.price - discount_amount
            old_price = self.price
            return new_price, old_price

        return self.price

    
     # Зберігаємо товар
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
    

    def get_material_info(self):
        materials = self.materials.all()
        return ", ".join([f"{m.material.article} | {m.material.name} | {m.material.metal} | {m.material.assay} | {m.material.color}" for m in materials]) if materials else "Матеріал не вибрано"

    # def __str__(self):
    #     translation = self.translations.first()  # перший переклад
    #     return translation.name if translation and translation.name else f"Product {self.id}"
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
    if not instance.qr_code:
        instance.qr_code = generate_qr_code(instance)




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