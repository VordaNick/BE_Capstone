# Generated by Django 5.1.4 on 2024-12-24 06:30

import library.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_alter_transaction_expected_return_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='expected_return_date',
            field=models.DateTimeField(default=library.models.calc_expected_return_date),
        ),
    ]