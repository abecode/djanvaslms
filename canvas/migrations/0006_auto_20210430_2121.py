# Generated by Django 3.0.8 on 2021-04-30 21:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('canvas', '0005_auto_20210430_2119'),
    ]

    operations = [
        migrations.RenameField(
            model_name='enrollment',
            old_name='roll',
            new_name='role',
        ),
    ]