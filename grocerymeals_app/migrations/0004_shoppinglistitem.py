# Generated by Django 2.2.3 on 2020-01-09 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grocerymeals_app', '0003_product_provider'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingListItem',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('product_id', models.CharField(max_length=50)),
            ],
        ),
    ]