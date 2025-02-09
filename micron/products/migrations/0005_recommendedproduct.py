

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_translations'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecommendedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='products.product')),
                ('recommended_products', models.ManyToManyField(to='products.product')),
            ],
        ),
    ]
