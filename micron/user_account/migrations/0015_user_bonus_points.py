# Generated by Django 5.1.4 on 2025-04-13 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_account", "0014_alter_contact_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="bonus_points",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
