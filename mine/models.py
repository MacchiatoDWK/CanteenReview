from django.db import models


# Create your models here.

class UserInfo(models.Model):
    Username = models.CharField(verbose_name="邮箱", max_length=20)
    Password = models.CharField(verbose_name="密码", max_length=20)
    UserType = models.IntegerField(verbose_name="用户类型")#1是用户，2是商家，3是管理员
    StallID = models.IntegerField(verbose_name="档口ID", null=True, blank=True)
    Name = models.CharField(verbose_name="昵称", max_length=10, null=True, blank=True)


class AuthMessage(models.Model):
    UserID = models.IntegerField(verbose_name="用户ID")
    Username = models.CharField(verbose_name="用户名", max_length=20)
    StallID = models.IntegerField(verbose_name="申请认证档口ID")
    Describe = models.TextField(verbose_name="申请描述", max_length=110)
    Validity = models.IntegerField(verbose_name="是否有效")#1是有效，0是无效
