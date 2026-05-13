from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0005_coupon_max_uses_coupon_used_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='code',
            field=models.CharField(
                help_text='Unique coupon code (for example: SAVE20, SUMMER2024)',
                max_length=50,
                unique=True,
            ),
        ),
    ]