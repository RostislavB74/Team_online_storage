# Generated by Django 5.1.5 on 2025-02-09 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_rename_desccription_gemstone_main_product_color_gemstone_main_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='dimenstions',
            new_name='dimensions',
        ),
        migrations.AddField(
            model_name='product',
            name='description_product',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='design_product',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
