from django.shortcuts import render, redirect
from addReview.models import Review, Image
from django.core.paginator import Paginator
from django.http import JsonResponse
from admin.models import CanteenInfo, StallInfo, DishInfo
# Create your views here.


def index(request):
    return render(request, 'index.html')

def get_comments(request):
    page = int(request.GET.get('page', 1))
    page_size = 10

    canteen = request.GET.get('canteen')
    stall = request.GET.get('stall')
    dish = request.GET.get('dish')

    reviews = Review.objects.all().order_by('-Timestamp')
    paginator = Paginator(reviews, page_size)
    page_obj = paginator.get_page(page)

    if canteen == "0":
        reviews = Review.objects.all().order_by('-Timestamp')
        paginator = Paginator(reviews, page_size)
        page_obj = paginator.get_page(page)
    elif stall == "0":
        reviews = Review.objects.filter(ObjType=1, ObjID=canteen).order_by('-Timestamp')
        paginator = Paginator(reviews, page_size)
        page_obj = paginator.get_page(page)
    elif dish ==  "0":
        reviews = Review.objects.filter(ObjType=2, ObjID=stall).order_by('-Timestamp')
        paginator = Paginator(reviews, page_size)
        page_obj = paginator.get_page(page)
    else :
        reviews = Review.objects.filter(ObjType=3, ObjID=dish).order_by('-Timestamp')
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
        })

    return JsonResponse({
        'comments': comment_data,
        'has_next': page_obj.has_next()
    })