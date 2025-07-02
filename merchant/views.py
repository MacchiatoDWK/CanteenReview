from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta, date
from addReview.models import Review, Image
from admin.models import StallInfo, CanteenInfo, DishInfo
from mine.models import UserInfo
from merchant.models import WeeklyReport
import json
from collections import Counter
import re

# Create your views here.

def get_stall_comments(request):
    page = int(request.GET.get('page', 1))
    page_size = 10
    userid = request.COOKIES.get('userid')
    user = UserInfo.objects.get(id=userid)
    my_stall = user.StallID
    my_dish = DishInfo.objects.filter(Stall_id=my_stall)
    reviews = Review.objects.filter(ObjType=2, ObjID=my_stall)

    for dish in my_dish:
        review2 = Review.objects.filter(ObjType=3, ObjID=dish.id)
        reviews = reviews.union(review2)

    order = request.GET.get("order", "time_desc")

    order_map = {
        "rating_asc": "Rating",
        "rating_desc": "-Rating",
        "time_asc": "Timestamp",
        "time_desc": "-Timestamp",
    }
    order_by = order_map.get(order, "-Timestamp")

    reviews = reviews.order_by(order_by)

    paginator = Paginator(reviews, page_size)
    page_obj = paginator.get_page(page)

    comment_data = []

    for review in page_obj:
        # 获取被评论对象名称
        if review.ObjType == 1:
            try:
                canteenName = CanteenInfo.objects.get(id=review.ObjID).CanteenName
                stallName = ""
                dishName = ""
            except:
                canteenName = "已删除食堂"
                stallName = ""
                dishName = ""
        elif review.ObjType == 2:
            try:
                canteenid = StallInfo.objects.get(id=review.ObjID).Canteen_id
                canteenName = CanteenInfo.objects.get(id=canteenid).CanteenName
                stallName = StallInfo.objects.get(id=review.ObjID).StallName
                dishName = ""
            except:
                canteenName = "已删除食堂"
                stallName = "已删除档口"
                dishName = ""
        elif review.ObjType == 3:
            try:
                stallid = DishInfo.objects.get(id=review.ObjID).Stall_id
                stallName = StallInfo.objects.get(id=stallid).StallName
                canteenid = StallInfo.objects.get(id=stallid).Canteen_id
                canteenName = CanteenInfo.objects.get(id=canteenid).CanteenName
                dishName = DishInfo.objects.get(id=review.ObjID).DishName
            except:
                canteenName = "已删除食堂"
                stallName = "已删除档口"
                dishName = "已删除菜品"
        else:
            canteenName = ""
            stallName = ""
            dishName = ""

        # 获取图片
        images = Image.objects.filter(ReviewID=review.id)
        image_urls = [img.ImageURL for img in images]

        # 构造返回数据
        comment_data.append({
            'username': review.Username,
            'rating': review.Rating,
            'text': review.Describe,
            'timestamp': review.Timestamp.strftime("%Y-%m-%d %H:%M"),
            'canteenName': canteenName,
            'stallName': stallName,
            'dishName': dishName,
            'images': image_urls,
            'reviewId':review.id,
        })

    return JsonResponse({
        'comments': comment_data,
        'has_next': page_obj.has_next()
    })


def get_rating_distribution(request):
    userid = request.COOKIES.get('userid')
    user = UserInfo.objects.get(id=userid)
    my_stall = user.StallID
    my_dish = DishInfo.objects.filter(Stall_id=my_stall)
    reviews = Review.objects.filter(ObjType=2, ObjID=my_stall)
    for dish in my_dish:
        review2 = Review.objects.filter(ObjType=3, ObjID=dish.id)
        reviews = reviews.union(review2)

    distribution = {str(i): 0 for i in range(1, 6)}

    # 遍历评论统计数量
    for review in reviews:
        rating = str(review.Rating)
        if rating in distribution:
            distribution[rating] += 1

    return JsonResponse({'distribution': distribution})


def get_dish_avg_scores(request):
    userid = request.COOKIES.get('userid')
    user = UserInfo.objects.get(id=userid)
    my_stall = user.StallID
    my_dish = DishInfo.objects.filter(Stall_id=my_stall)

    result = []

    for dish in my_dish:
        reviews = Review.objects.filter(ObjType='3', ObjID=dish.id)
        ratings = [r.Rating for r in reviews]
        if ratings:
            avg = round(sum(ratings) / len(ratings), 2)
        else:
            avg = 0

        result.append({
            'dish_name': dish.DishName,
            'avg_rating': avg,
        })

    return JsonResponse({'dishes': result})