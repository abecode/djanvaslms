# Generated by Django 3.2.5 on 2022-01-08 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canvas', '0010_auto_20210502_0432'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='api_id',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
    ]
