# Generated by Django 3.2.5 on 2022-03-24 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canvas', '0002_auto_20220324_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pull',
            name='ts',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
