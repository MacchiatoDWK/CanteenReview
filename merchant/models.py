from django.db import models

# Create your models here.

class WeeklyReport(models.Model):
    StallID = models.IntegerField(verbose_name="档口ID")
    StartDate = models.DateField(verbose_name="开始日期")
    EndDate = models.DateField(verbose_name="结束日期")
    TotalReviews = models.IntegerField(verbose_name="总评论数")
    AverageRating = models.FloatField(verbose_name="平均评分")
    HighRatingCount = models.IntegerField(verbose_name="好评数量")  # 评分4-5
    MidRatingCount = models.IntegerField(verbose_name="中评数量")   # 评分2-3
    LowRatingCount = models.IntegerField(verbose_name="差评数量")   # 评分0-1
    CommonKeywords = models.TextField(verbose_name="常见关键词", null=True, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
