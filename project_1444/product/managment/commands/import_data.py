import pandas as pd
from django.core.management.base import BaseCommand
from product.models import Product, Category  # Імпортуємо моделі

class Command(BaseCommand):
    help = "Import products from Excel file"

    def handle(self, *args, **kwargs):
        file_path = "data/products.xlsx"  # Вкажіть шлях до вашого файлу

        # Завантажуємо Excel у DataFrame
        df = pd.read_excel(file_path, engine="openpyxl")

        for _, row in df.iterrows():
            # Отримуємо або створюємо категорію
            category, _ = Category.objects.get_or_create(name=row["Category"])

            # Додаємо продукт у базу
            Product.objects.create(
                name=row["Name"],
                category=category,
                price=row["Price"],
                weight=row["Weight"],
                description=row["Description"]
            )

        self.stdout.write(self.style.SUCCESS("Data imported successfully!"))
