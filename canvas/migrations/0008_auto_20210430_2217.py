# Generated by Django 3.0.8 on 2021-04-30 22:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('canvas', '0007_auto_20210430_2207'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('user', 'course', 'type')},
        ),
    ]