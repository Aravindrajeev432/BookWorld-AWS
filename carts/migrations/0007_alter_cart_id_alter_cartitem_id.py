# Generated by Django 4.1.1 on 2023-01-05 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0006_cartitem_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
