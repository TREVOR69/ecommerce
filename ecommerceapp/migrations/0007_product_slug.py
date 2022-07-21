# Generated by Django 4.0.6 on 2022-07-18 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0006_remove_product_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(default=4546, unique=True),
            preserve_default=False,
        ),
    ]