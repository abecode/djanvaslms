# Generated by Django 3.2.5 on 2022-04-01 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('canvas', '0006_qualitativereview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qualitativereview',
            name='course_section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='canvas.coursesection'),
        ),
    ]