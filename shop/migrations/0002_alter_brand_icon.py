# Generated by Django 4.0.4 on 2022-06-06 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='icon',
            field=models.ImageField(blank=True, upload_to='brands'),
        ),
    ]
