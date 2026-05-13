from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0019_alter_user_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='region',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='profile',
            name='city',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='post_office',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
    ]
