from django.db import models
# Create your models here.


class CanteenInfo(models.Model):
    CanteenName = models.CharField(max_length=20)


class StallInfo(models.Model):
    StallName = models.CharField(max_length=100,unique=True)
    Canteen = models.ForeignKey(CanteenInfo, on_delete=models.CASCADE)


class DishInfo(models.Model):
    DishName = models.CharField(max_length=100)
    Stall = models.ForeignKey(StallInfo, on_delete=models.CASCADE)
    Description = models.TextField()