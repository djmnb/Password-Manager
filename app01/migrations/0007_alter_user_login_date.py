# Generated by Django 4.0.4 on 2022-05-30 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0006_alter_user_login_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='login_date',
            field=models.CharField(max_length=30, verbose_name='上次登录时间'),
        ),
    ]