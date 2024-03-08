import datetime

import django
from django.db import models


# Create your models here.


class User(models.Model):

    name = models.CharField(max_length=50,verbose_name="账号")
    password = models.CharField(max_length=50,verbose_name="密码")
    email = models.CharField(max_length=50,verbose_name="邮箱",null=True,blank=True)
    ip = models.CharField(max_length=20,verbose_name="上次访问ip地址",default="127.0.0.1")
    login_date = models.CharField(verbose_name="上次登录时间",max_length=30)

    def __str__(self):
        return f"{self.name}"


class Password(models.Model):
    name = models.CharField(max_length=50,verbose_name="账号")
    password = models.CharField(max_length=50,verbose_name="密码")
    user = models.ForeignKey(to=User,verbose_name="用户",on_delete=models.CASCADE,related_name="user")



