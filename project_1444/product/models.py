import uuid
from decimal import Decimal
from io import BytesIO

import qrcode
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from users.models import User
from utils.multi_backend_image_field import (
    MultiBackendImageField,
    MultiBackendFileField,
)
from .utils import save_with_translation


class Categories(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name="Categories"),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )
    updated_at = models.DateTimeField(auto_now=True)
    has_length = models.BooleanField(default=False, verbose_name=_("Має довжину (см)"))
    has_width = models.BooleanField(default=False, verbose_name=_("Має ширину (см)"))
    has_diameter = models.BooleanField(
        default=False, verbose_name=_("Має діаметр (мм)")
    )
    has_weight = models.BooleanField(default=True, verbose_name=_("Має вагу (г)"))

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = _("Категорія виробу")
        verbose_name_plural = _("Категорії виробів")

    def __str__(self):
        return self.safe_translation_getter(
            "name", default=_("Без назви")
        )  # Бере name із перекладу


class Weaving(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name="Weaving"),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = _("Плетіння")
        verbose_name_plural = _("Плетіння")

    def __str__(self):
        return self.safe_translation_getter(
            "name", default=_("Без назви")
        )  # Бере name із перекладу


class Clasp(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name="Clasp"),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = _("Застібка")
        verbose_name_plural = _("Застібки")

    def __str__(self):
        return self.safe_translation_getter("name", default=_("Без назви"))


class Coating(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name="Coating"),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = _("Покриття")
        verbose_name_plural = _("Покриття")

    def __str__(self):
        return self.safe_translation_getter("name", default=_("Без назви"))


class SubCategories(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )
    parent = models.ForeignKey(
        Categories,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = _("Підкатегорія виробу")
        verbose_name_plural = _("Підкатегорії виробів")

    def __str__(self):
        return self.safe_translation_getter("name", default=_("Без назви"))


class Colors(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name="Colors"),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = _("Колір")
        verbose_name_plural = _("Кольори")

    def __str__(self):
        return self.safe_translation_getter(
            "name", default=_("Без назви")
        )  # Бере name із перекладу


class Collections(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name="Collections"),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = _("Колекція")
        verbose_name_plural = _("Колекції")

    def __str__(self):
        return self.safe_translation_getter(
            "name", default=_("Без назви")
        )  # Бере name із перекладу


class Designs(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name="Designs"),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = _("Дизайн")
        verbose_name_plural = _("Дизайни")

    def __str__(self):
        return self.safe_translation_getter(
            "name", default=_("Без назви")
        )  # Бере name із перекладу


class Styles(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, verbose_name="Styles"),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = _("Стиль")
        verbose_name_plural = _("Стилі")

    def __str__(self):
        return self.safe_translation_getter("name", default=_("Без назви"))


class Material(TranslatableModel):
    PROBE_CHOICES = [
        ("0", "0"),
        ("585", "585"),
        ("750", "750"),
        ("925", "925"),
        ("950", "950"),
    ]

    COLOR_CHOICES = [
        ("white", "white"),
        ("yellow", "yellow"),
        ("red", "red"),
        ("brown", "brown"),
        ("rhodium_plating", "rhodium_plating"),
        ("black", "black"),
        ("blackening", "blackening"),
    ]

    METAL_CHOICES = [
        ("gold", "gold"),
        ("silver", "silver"),
        ("platinum", "platinum"),
        ("steel", "steel"),
    ]

    material = models.CharField(
        max_length=50, choices=METAL_CHOICES, null=True, blank=True
    )
    assay = models.CharField(
        max_length=20, choices=PROBE_CHOICES, null=True, blank=True
    )
    color = models.CharField(
        max_length=50, choices=COLOR_CHOICES, null=True, blank=True
    )
    article = models.CharField(max_length=20, unique=True, blank=True, null=True)
    translations = TranslatedFields(
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
        material_name=models.CharField(max_length=50),
        color_name=models.CharField(max_length=50),
    )

    class Meta:
        verbose_name = _("Матеріал")
        verbose_name_plural = _("Матеріали")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Оновлюємо перекладені поля при збереженні
        self.set_current_language("uk")
        self.material_name = {
            "gold": "Золото",
            "silver": "Срібло",
            "platinum": "Платина",
            "steel": "Сталь",
        }.get(self.material, self.material)
        self.color_name = {
            "white": "Білий",
            "yellow": "Жовтий",
            "red": "Червоний",
            "brown": "Коричневий",
            "rhodium_plating": "Родіювання",
            "black": "Чорний",
            "blackening": "Чорніння",
        }.get(self.color, self.color)
        self.set_current_language("en")
        self.material_name = self.material
        self.color_name = self.color
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.material_name} | {self.assay} | {self.color_name}"


# Матеріали
# class Material(TranslatableModel):

#     PROBE_CHOICES = [
#         ("0", "0"),
#         ("585", "585"),
#         ("750", "750"),
#         ("925", "925"),
#         ("950", "950"),
#     ]
#     COLOR_CHOICES = [
#         ("white", _("White")),  # Переклад буде в .po файлах
#         ("yellow", _("Yellow")),
#         ("red", _("Red")),
#         ("brown", _("Brown")),
#         ("rhodium_plating", _("Rhodium Plating")),
#         ("black", _("Black")),
#         ("blackening", _("Blackening")),
#     ]

#     METAL_CHOICES = [
#         ("gold", _("Gold")),
#         ("silver", _("Silver")),
#         ("platinum", _("Platinum")),
#         ("steel", _("Steel")),
#     ]
#     # COLOR_CHOICES = [
#     #     ("white", "Білий"),
#     #     ("yellow", "Жовтий"),
#     #     ("red", "Червоний"),
#     #     ("brown", "Коричневий"),
#     #     ("rhodium_plating", "Родіювання"),
#     #     ("black", "Чорний"),
#     #     ("blackening", "Чорніння"),
#     # ]
#     # METAL_CHOICES = [
#     #     ("gold", "Золото"),
#     #     ("silver", "Срібло"),
#     #     ("platinum", "Платина"),
#     #     ("steel", "Сталь"),
#     # ]
#     material = models.CharField(
#         max_length=50, choices=METAL_CHOICES, null=True, blank=True
#     )
#     assay = models.CharField(
#         max_length=20, choices=PROBE_CHOICES, null=True, blank=True
#     )
#     color = models.CharField(
#         max_length=50, choices=COLOR_CHOICES, null=True, blank=True
#     )
#     article = models.CharField(max_length=20, unique=True, blank=True, null=True)
#     translations = TranslatedFields(
#         slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
#     )

#     class Meta:
#         verbose_name = "Матеріал"
#         verbose_name_plural = "Матеріали"

#     # def __str__(self):
#     #     material = f"{self.material} | {self.assay} | {self.color}"
#     #     return material
#     def __str__(self):
#         # Отримуємо перекладені значення
#         material_display = self.get_material_display()
#         color_display = self.get_color_display()
#         return f"{material_display} | {self.assay} | {color_display}"


# Gemstone
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
        slug=models.SlugField(unique=True),
    )

    type = models.CharField(
        max_length=20, choices=TypeGemstones.choices, null=True, blank=True
    )
    origin_stone = models.CharField(
        max_length=20, choices=Origin.choices, null=True, blank=True
    )
    level = models.CharField(
        max_length=20, choices=OrderLevel.choices, null=True, blank=True
    )
    # color = models.ForeignKey('Colors', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Ювелірний камінь")
        verbose_name_plural = _("Ювелірне каміння")

    def __str__(self):
        return self.safe_translation_getter("name", default=_("Без назви"))

    def clean(self):
        """Валідація категорій каменів"""
        if self.origin_stone == Origin.SYNTHETIC and self.level:
            raise ValidationError({"level": _("Синтетичні камені не мають порядку.")})

        if self.type == TypeGemstones.PRECIOUS and self.level not in [
            OrderLevel.PRECIOUS_I,
            OrderLevel.PRECIOUS_II,
            OrderLevel.PRECIOUS_III,
            OrderLevel.PRECIOUS_IV,
        ]:
            raise ValidationError(
                {"level": _("Дорогоцінні камені мають рівні I-IV порядку.")}
            )

        if self.type == TypeGemstones.SEMIPRECIOUS and self.level not in [
            OrderLevel.SEMI_PRECIOUS_I,
            OrderLevel.SEMI_PRECIOUS_II,
        ]:
            raise ValidationError(
                {"level": _("Напівкоштовні камені мають рівні I-II порядку.")}
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Occasion(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True),
        slug=models.SlugField(max_length=50, unique=True, blank=True),
    )

    class Meta:
        verbose_name = _("Привід")
        verbose_name_plural = _("Приводи")

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter(
            "name", default=_("Без назви")
        )  # Бере name із перекладу


class Gender(models.Model):
    GENDER_CHOICES = [
        ("female", _("Жіноче")),
        ("male", _("Чоловіче")),
        ("children", _("Дитяче")),
        ("unisex", _("Унісекс")),
    ]
    name = models.CharField(choices=GENDER_CHOICES, max_length=20)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Для кого")
        verbose_name_plural = _("Для кого")

    def __str__(self):
        return self.name


class SubProducts(models.Model):
    parent_product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Продукт"),
    )
    position = models.IntegerField(null=True, blank=True)
    article = models.CharField(max_length=50, unique=True, blank=True, null=True)
    ean_13 = models.CharField(max_length=13, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Ціна"))
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("100.0")),
        ],
    )
    new_price = models.FloatField(null=True, blank=True)
    old_price = models.FloatField(null=True, blank=True)
    qr_code = models.ImageField(upload_to="qrcodes/", blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    length = models.FloatField(null=True, blank=True, verbose_name=_("Довжина (см)"))
    max_length = models.FloatField(
        null=True, blank=True, verbose_name=_("Макс. довжина (см)")
    )
    width = models.FloatField(null=True, blank=True, verbose_name=_("Ширина (см)"))
    size = models.FloatField(null=True, blank=True, verbose_name=_("Розмір(мм) "))
    weight = models.FloatField(null=True, blank=True, verbose_name=_("Вага (г)"))

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

    def get_length_display(self):
        """Формує правильне відображення довжини"""
        if self.length and self.max_length:
            return "{}-{} {}".format(self.length, self.max_length, _("см"))
        elif self.length:
            return "{} {}".format(self.length, _("см"))
        return _("Невідомо")

    def save(self, *args, **kwargs):
        # Автоматично встановлює порядковий номер для кожного продукту
        if not self.pk:  # Якщо створюється новий запис
            last_subproduct = (
                SubProducts.objects.filter(parent_product=self.parent_product)
                .order_by("position")
                .last()
            )
            self.position = (last_subproduct.position + 1) if last_subproduct else 1

        # 💸 Логіка обчислення знижки
        if self.discount_percentage:
            discount = float(self.discount_percentage)
            self.old_price = float(self.price)
            self.new_price = round(float(self.price) * (1 - discount / 100), 2)
        else:
            self.old_price = None
            self.new_price = None

        super().save(*args, **kwargs)

    def __str__(self):
        details = []
        if self.length:
            details.append("Довжина: {} см".format(self.length))
        if self.width:
            details.append("Ширина: {} см".format(self.width))
        if self.size:
            details.append("Розмір: {} мм".format(self.size))
        if self.weight:
            details.append("Вага: {} г".format(self.weight))

        details_str = ", ".join(details) if details else _("Без характеристик")
        return f"{self.parent_product.name} ({details_str})"


def generate_subarticle(product):
    last_product = SubProducts.objects.order_by("-id").first()
    if last_product:
        # Припустимо, що перші два символи - це префікс
        last_article_number = int(last_product.article[4:])
        new_article = (
            f"SBPR{last_article_number + 1:05d}"  # Формат: PR00001, PR00002, ...
        )
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


class ProductAttributes(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="attributes"
    )
    gender = models.CharField(
        "Gender",
        max_length=20,
        choices=Gender.GENDER_CHOICES,
        default="unisex",
        blank=True,
    )
    color_coating = models.ForeignKey(
        "Colors", on_delete=models.SET_NULL, null=True, blank=True
    )
    weaving_type = models.ForeignKey(
        "Weaving", on_delete=models.SET_NULL, null=True, blank=True
    )
    coating_material = models.ForeignKey(
        "Coating", on_delete=models.SET_NULL, null=True, blank=True
    )
    style = models.ForeignKey(
        "Styles", on_delete=models.SET_NULL, null=True, blank=True
    )
    clasp_type = models.ForeignKey(
        "Clasp", on_delete=models.SET_NULL, null=True, blank=True
    )


class ProductStatus(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    def __str__(self):
        return self.name


class ProductMaterial(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="materials"
    )
    material = models.ForeignKey(
        "Material", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_primary = models.BooleanField(default=False)  # Чи основний матеріал
    set_included = models.BooleanField(default=False)

    class Meta:
        unique_together = ("product", "material")  # Уникнення дублювань

    def __str__(self):
        return f"{self.product} - {self.material}"


class ProductGemstone(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="gemstones"
    )
    gemstone = models.ForeignKey(
        "Gemstone", on_delete=models.CASCADE, null=True, blank=True
    )
    color = models.ForeignKey(
        "Colors", on_delete=models.SET_NULL, null=True, blank=True
    )  # Колір каменю
    weight = models.FloatField(null=True, blank=True)  # Вага каменю
    is_main = models.BooleanField(default=False)  # Основний камінь
    set_included = models.BooleanField(default=False)  # Камінь в комплекті
    description = models.ForeignKey(
        "Descriptions", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = (
            "product",
            "gemstone",
            "color",
        )  # Один і той самий камінь може бути різного кольору

    def clean(self):
        """Забезпечуємо, що тільки один камінь у виробі є основним."""
        if self.is_main:
            existing_main = ProductGemstone.objects.filter(
                product=self.product, is_main=True
            ).exclude(pk=self.pk)
            if existing_main.exists():
                raise ValidationError(_("У виробі вже є основний камінь!"))

    def save(self, *args, **kwargs):
        self.clean()  # Викликаємо перевірку перед збереженням
        super().save(*args, **kwargs)

    def __str__(self):
        is_main = _("Основний") if self.is_main else _("Додатковий")
        return f"{self.product} - {self.gemstone} ({self.color}, {self.weight}g, {is_main})"


class ProductImage(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images"
    )
    # image = CloudinaryField("image")
    image = MultiBackendImageField(
        upload_to="image/", blank=True, null=True, max_length=500
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Фото продукції")
        verbose_name_plural = _("Фото продукцій")

    def __str__(self):
        return f"{self.product.article} - Image"


class ProductCertificate(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="certificates"
    )
    file = MultiBackendFileField(upload_to="file/", blank=True, null=True)
    # file = CloudinaryField("file")  # Змінюємо на CloudinaryField
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Сертифікат продукції")
        verbose_name_plural = _("Сертифікати продукцій")

    def __str__(self):
        return f"{self.product.article} - Certificate"


class Descriptions(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
        text=models.TextField(null=True, blank=True),
        seo_title=models.CharField(max_length=255, null=True, blank=True),
        seo_description=models.TextField(null=True, blank=True),
        keywords=models.CharField(max_length=500, null=True, blank=True),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Description")
        verbose_name_plural = _("Descriptions")

    def save(self, *args, **kwargs):
        name = self.safe_translation_getter("name")
        if not self.safe_translation_getter("slug") and name:
            self.set_current_language(self.get_current_language())
            self.slug = slugify(name)
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.safe_translation_getter("name")
        return name if name is not None else _("Description {}").format(self.id)


class Product(TranslatableModel):
    description = models.ManyToManyField(
        "Descriptions", blank=True, related_name="products"
    )
    category = models.ForeignKey(
        "Categories", on_delete=models.SET_NULL, null=True, blank=True
    )
    subproducts = models.ManyToManyField(
        "SubProducts", related_name="subproducts", blank=True
    )
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True, null=True, blank=True),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )
    subcategory = models.ForeignKey(
        "SubCategories", on_delete=models.SET_NULL, null=True, blank=True
    )
    statuses = models.ManyToManyField(
        "ProductStatus", blank=True, related_name="status"
    )
    collection = models.ForeignKey(
        "Collections", on_delete=models.SET_NULL, null=True, blank=True
    )
    design = models.ForeignKey(
        "Designs", on_delete=models.SET_NULL, null=True, blank=True
    )
    occasions = models.ManyToManyField("Occasion", blank=True, related_name="occasion")
    article = models.CharField(max_length=50, unique=True, blank=True, null=True)
    ean_13 = models.CharField(max_length=13, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    year_collection = models.IntegerField(null=True, blank=True)
    country_of_origin = models.CharField(max_length=255, null=True, blank=True)
    is_ukrainian_cashback = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    @property
    def name_property(self):
        return self.safe_translation_getter("name", default=_("Без назви"))

    @property
    def slug_property(self):
        return self.safe_translation_getter("slug", default=_("Без опису"))

    def __str__(self):
        translation = self.safe_translation_getter("name", any_language=True)
        return translation if translation else f"Product {self.id}"


# Функція для генерації `sku`
def generate_sku():
    return f"SKU-{uuid.uuid4().hex[:8].upper()}"


# Функція для генерації `article`
def generate_product_new_article(product=None):

    # def generate_sku():
    last_product = Product.objects.order_by("-id").first()
    if last_product:
        # Припустимо, що перші два символи - це префікс
        last_article_number = int(last_product.article[2:])
        new_article = (
            f"PR{last_article_number + 1:05d}"  # Формат: PR00001, PR00002, ...
        )
    else:
        new_article = "PR00001"  # Початковий SKU
    return new_article


# Функція для генерації QR-коду
def generate_qr_code(product):
    """Генерує QR-код із `sku` або `ean_13`"""
    qr_data = product.sku or product.ean_13 or product.name
    qr = qrcode.make(qr_data)
    qr_io = BytesIO()
    qr.save(qr_io, format="PNG")
    qr_file = ContentFile(qr_io.getvalue(), name=f"qr_{product.sku}.png")
    return qr_file


class RingSizeConversion(models.Model):
    circumference_mm = models.FloatField(unique=True)  # Довжина кола
    diameter_mm = models.FloatField()  # Діаметр каблучки
    size_ua = models.CharField(max_length=10)  # Український розмір
    size_us = models.CharField(max_length=10, null=True, blank=True)  # США, Канада
    size_eu = models.CharField(max_length=10, null=True, blank=True)  # Європа
    size_uk = models.CharField(
        max_length=10, null=True, blank=True
    )  # Англія, Ірландія, Австралія
    size_asia = models.CharField(max_length=10, null=True, blank=True)  # Азія
    size_other_eu = models.CharField(
        max_length=10, null=True, blank=True
    )  # Решта Європи

    class Meta:
        verbose_name = _("Конвертація розмірів")
        verbose_name_plural = _("Конвертер розмірів")

    def __str__(self):
        return f"{self.circumference_mm} мм → {self.size_ua} (UA)"


def save(self, *args, **kwargs):
    if (
        self.category
        and self.category.name.lower() == _("каблучки")
        and self.circumference_mm
    ):
        # Автоматично визначаємо розмір
        size_obj = RingSizeConversion.objects.filter(
            circumference_mm=self.circumference_mm
        ).first()
        if size_obj:
            self.size = size_obj.size_ua  # Вибираємо український розмір
    super().save(*args, **kwargs)
