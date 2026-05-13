from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("coupons", "0006_coupon_code_unique"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="coupon",
            index=models.Index(
                fields=["active", "valid_from", "valid_to"],
                name="coupon_lookup_idx",
            ),
        ),
    ]
