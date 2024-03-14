# Generated by Django 4.2 on 2024-03-14 09:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0011_alter_profile_is_email_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='profile',
            name='is_email_verified',
            field=models.BooleanField(default=False),
        ),
    ]
