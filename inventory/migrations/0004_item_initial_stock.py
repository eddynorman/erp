# Generated by Django 3.2.19 on 2025-03-30 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_item_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='initial_stock',
            field=models.IntegerField(default=0),
        ),
    ]
