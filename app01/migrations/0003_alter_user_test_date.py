# Generated by Django 4.0.4 on 2022-05-30 08:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_user_test_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='test_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='dfs'),
        ),
    ]
