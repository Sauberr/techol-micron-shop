# Generated by Django 5.0 on 2023-12-17 21:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_account", "0002_alter_user_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="avatar"),
        ),
    ]
