# Generated by Django 3.1 on 2022-09-01 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20220831_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='discount',
            field=models.IntegerField(default='0'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='total_after_discount',
            field=models.IntegerField(default='0'),
            preserve_default=False,
        ),
    ]