# Generated by Django 4.2 on 2024-03-19 18:07

from django.db import migrations
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_recommendedproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producttranslation',
            name='description',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='text',
            field=django_ckeditor_5.fields.CKEditor5Field(),
        ),
        migrations.DeleteModel(
            name='RecommendedProduct',
        ),
    ]
