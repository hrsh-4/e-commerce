# Generated by Django 2.2.4 on 2019-12-16 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='item_quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]