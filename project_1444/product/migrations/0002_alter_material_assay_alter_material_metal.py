# Generated by Django 5.1.5 on 2025-02-09 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='assay',
            field=models.CharField(blank=True, choices=[('585', '585'), ('750', '750'), ('925', '925'), ('950', '950')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='metal',
            field=models.CharField(choices=[('gold', 'Золото'), ('silver', 'Срібло'), ('platinum', 'Платина'), ('steel', 'Сталь')], max_length=50),
        ),
    ]
