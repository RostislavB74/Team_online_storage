# Generated by Django 5.1.5 on 2025-02-12 05:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_gender_occasion_product_gender_product_occasions'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gender',
            options={'ordering': ['name'], 'verbose_name': 'Для кого', 'verbose_name_plural': 'Для кого'},
        ),
    ]
