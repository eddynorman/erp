# Generated by Django 3.2.19 on 2025-03-24 19:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_name', models.CharField(max_length=100)),
                ('employee_email', models.EmailField(max_length=254)),
                ('employee_phone', models.CharField(max_length=16)),
                ('employee_address', models.CharField(max_length=200)),
                ('employee_designation', models.CharField(max_length=100)),
                ('employee_salary', models.FloatField()),
                ('employee_status', models.CharField(default='Active', max_length=100)),
                ('employee_branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.branch')),
                ('employee_department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.department')),
            ],
        ),
    ]
