# Generated by Django 2.2.3 on 2020-01-16 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grocerymeals_app', '0008_auto_20200115_0143'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=500)),
                ('email', models.CharField(max_length=500)),
                ('feedback', models.TextField()),
            ],
        ),
    ]