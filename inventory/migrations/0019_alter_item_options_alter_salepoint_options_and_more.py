# Generated by Django 5.2 on 2025-05-06 09:31

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "company",
            "0007_employee_first_name_employee_last_name_employee_user_and_more",
        ),
        ("inventory", "0018_remove_issueditem_total_cost"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="item",
            options={
                "ordering": ["name"],
                "verbose_name": "Item",
                "verbose_name_plural": "Items",
            },
        ),
        migrations.AlterModelOptions(
            name="salepoint",
            options={
                "ordering": ["name"],
                "verbose_name": "Sale Point",
                "verbose_name_plural": "Sale Points",
            },
        ),
        migrations.AlterModelOptions(
            name="store",
            options={
                "ordering": ["name"],
                "verbose_name": "Store",
                "verbose_name_plural": "Stores",
            },
        ),
        migrations.AlterModelOptions(
            name="supplier",
            options={
                "ordering": ["name"],
                "verbose_name": "Supplier",
                "verbose_name_plural": "Suppliers",
            },
        ),
    ]
