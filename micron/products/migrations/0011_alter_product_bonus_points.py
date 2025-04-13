# Generated by Django 5.1.4 on 2025-04-13 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0010_product_bonus_points"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="bonus_points",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=0, max_digits=10, null=True
            ),
        ),
    ]
