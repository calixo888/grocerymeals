# Generated by Django 2.2.3 on 2020-01-11 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grocerymeals_app', '0005_auto_20200109_0807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
