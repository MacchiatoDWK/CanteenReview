from django.db import models

# Create your models here.


class Ranking(models.Model):
    name = models.CharField(max_length=255)  # 商家名称
    reviews_count = models.IntegerField()    # 评论数
    rating = models.FloatField()             # 评分
    location = models.CharField(max_length=255)  # 地点
    specialties = models.CharField(max_length=255)  # 特色菜

    def __str__(self):
        return self.name
