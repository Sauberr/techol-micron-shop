# Generated by Django 4.2 on 2024-02-03 16:20

from django.db import migrations
from django_ckeditor_5.fields import CKEditor5Field


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_review"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="description",
            field=CKEditor5Field(config_name='extends', blank=True, null=True),
        ),
    ]
