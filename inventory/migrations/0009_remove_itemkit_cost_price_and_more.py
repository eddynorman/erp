# Generated by Django 5.2 on 2025-04-05 20:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0008_itemkit_cost_price"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="itemkit",
            name="cost_price",
        ),
        migrations.RemoveField(
            model_name="itemotherunit",
            name="conversion_factor",
        ),
        migrations.AddField(
            model_name="itemotherunit",
            name="buying_price",
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="itemotherunit",
            name="selling_price",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="itemotherunit",
            name="smallest_units",
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
