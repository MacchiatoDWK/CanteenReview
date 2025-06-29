from django.db import models

# Create your models here.
class Review(models.Model):

    UserID = models.IntegerField(verbose_name="用户ID")
    Username = models.CharField(verbose_name="用户名", max_length=40)
    Rating = models.IntegerField(verbose_name="评分")
    Describe = models.TextField(verbose_name="评论内容", max_length=110)
    Timestamp = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    ObjType = models.IntegerField(verbose_name="被评价对象类型")
    ObjID = models.IntegerField(verbose_name="被评价对象ID")

class Image(models.Model):
    ReviewID = models.IntegerField(verbose_name="评论ID")
    ImageURL = models.CharField(verbose_name="图片地址", max_length=255)