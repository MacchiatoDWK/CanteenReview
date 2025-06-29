from django.shortcuts import render, get_object_or_404
from admin.models import DishInfo, StallInfo, CanteenInfo
from addReview.models import Review, Image
from django.db.models import Q


def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = DishInfo.objects.filter(
            Q(DishName__icontains=query) |
            Q(Description__icontains=query) |
            Q(Stall__StallName__icontains=query)
        ).distinct()
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search.html', context)


def detail(request, item_id):
    # 获取指定菜品
    item = get_object_or_404(DishInfo, id=item_id)

    # 获取该菜品对应的评论，ObjType=3代表菜品，ObjID是菜品id
    reviews = Review.objects.filter(ObjType=3, ObjID=item.id).order_by('-Timestamp')

    count = reviews.count()

    comment_data = []

    for review in reviews:
        images = Image.objects.filter(ReviewID=review.id)
        image_urls = [img.ImageURL for img in images]

        # 构造返回数据
        comment_data.append({
            'Username': review.Username,
            'Rating': review.Rating,
            'Describe': review.Describe,
            'Timestamp': review.Timestamp.strftime("%Y-%m-%d %H:%M"),
            'Images': image_urls,
        })


    context = {
        'item': item,
        'reviews': comment_data,  # 传给模板用小写reviews更通用
        'count': count,
    }
    return render(request, 'detail.html', context)