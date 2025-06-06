# Generated by Django 3.2.19 on 2025-03-24 19:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0004_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('to_shop', models.BooleanField(default=True)),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issue_approved_by', to='company.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('bar_code', models.CharField(max_length=20)),
                ('store_stock', models.IntegerField(default=0)),
                ('shop_stock', models.IntegerField(default=0)),
                ('status', models.CharField(default='Active', max_length=20)),
                ('buying_price', models.FloatField(default=0)),
                ('selling_price', models.FloatField(default=0)),
                ('smallest_unit', models.CharField(max_length=20)),
                ('is_sellable', models.BooleanField(default=True)),
                ('minimum_stock', models.IntegerField(default=0)),
                ('optimum_stock', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.category')),
            ],
        ),
        migrations.CreateModel(
            name='ItemKit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('status', models.CharField(default='Active', max_length=20)),
                ('selling_price', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ReceivedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('unit_price', models.FloatField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.item')),
            ],
        ),
        migrations.CreateModel(
            name='Requisition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('approved', models.BooleanField(default=False)),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requisition_approved_by', to='company.employee')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.department')),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=200)),
                ('contact_person', models.CharField(max_length=200)),
                ('contact_number', models.CharField(max_length=20)),
                ('status', models.CharField(default='Active', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=200)),
                ('contact_number', models.CharField(max_length=20)),
                ('status', models.CharField(default='Active', max_length=20)),
                ('contact_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.employee')),
            ],
        ),
        migrations.CreateModel(
            name='RequisitionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.item')),
                ('requisition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.requisition')),
            ],
        ),
        migrations.AddField(
            model_name='requisition',
            name='items',
            field=models.ManyToManyField(through='inventory.RequisitionItem', to='inventory.Item'),
        ),
        migrations.AddField(
            model_name='requisition',
            name='user_responsible',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.employee'),
        ),
        migrations.CreateModel(
            name='Receiving',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('is_store', models.BooleanField(default=True)),
                ('items', models.ManyToManyField(through='inventory.ReceivedItem', to='inventory.Item')),
                ('requisition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.requisition')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.supplier')),
                ('user_responsible', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.employee')),
            ],
        ),
        migrations.AddField(
            model_name='receiveditem',
            name='receiving',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.receiving'),
        ),
        migrations.CreateModel(
            name='ItemKitItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.item')),
                ('item_kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.itemkit')),
            ],
        ),
        migrations.AddField(
            model_name='itemkit',
            name='items',
            field=models.ManyToManyField(through='inventory.ItemKitItem', to='inventory.Item'),
        ),
        migrations.CreateModel(
            name='IssuedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.issue')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.item')),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='items',
            field=models.ManyToManyField(through='inventory.IssuedItem', to='inventory.Item'),
        ),
        migrations.AddField(
            model_name='issue',
            name='requested_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.employee'),
        ),
        migrations.AddField(
            model_name='issue',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.store'),
        ),
        migrations.CreateModel(
            name='Adjustment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('reason', models.TextField()),
                ('in_store', models.BooleanField(default=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.item')),
                ('user_responsible', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.employee')),
            ],
        ),
    ]
