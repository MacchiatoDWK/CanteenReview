from django.shortcuts import render
from summary.models import Ranking
from admin.models import CanteenInfo, StallInfo, DishInfo
from addReview.models import Review
from django.db.models import Avg, Count
from mine.models import UserInfo
import random  # 导入随机模块

def display_data(request):
    # 查询数据库中的所有数据
    canteens = CanteenInfo.objects.all()
    stalls = StallInfo.objects.all()
    dishes = DishInfo.objects.all()

    # 将查询到的数据传递到模板
    return render(request, 'display_data.html', {
        'canteens': canteens,
        'stalls': stalls,
        'dishes': dishes,
    })

def ranking (request):
    return render(request,'ranking.html')

def ranking_sumup(request):
    # 设置默认的用户类型和档口ID
    user_type = '商家'  # 默认为商家
    stall_id = 1  # 默认为档口ID 4

    # 获取该档口的菜品
    dishes = DishInfo.objects.filter(Stall_id=stall_id)

    # 用来存储每个菜品的评分、评论数和分类
    dish_ratings = []

    # 获取该档口的评分数据
    stall_reviews = Review.objects.filter(ObjType=1, ObjID=stall_id)  # 获取档口类型的评论
    average_rating = stall_reviews.aggregate(Avg('Rating'))['Rating__avg'] or 0

    for dish in dishes:
        reviews = Review.objects.filter(ObjType=2, ObjID=dish.id)  # 过滤出菜品的所有评论
        avg_rating = reviews.aggregate(Avg('Rating'))['Rating__avg'] or 0
        review_count = reviews.count()

        # 根据评分进行分类
        if avg_rating >= 4:
            category = '优秀'
        elif 3 <= avg_rating < 4:
            category = '合格'
        else:
            category = '不合格'

        # 根据菜品评分生成个性化总结
        if avg_rating >= 4:
            dish_summary = random.choice([
                f"{dish.DishName} 口味绝佳，深受顾客喜爱，继续保持高品质！",
                f"{dish.DishName} 在顾客中的口碑很好，火候掌握得相当到位，继续加油！"
            ])
        elif 3 <= avg_rating < 4:
            dish_summary = random.choice([
                f"{dish.DishName} 的口味和火候还有提升空间，建议加强菜品的一致性。",
                f"{dish.DishName} 在顾客中的评价比较平衡，建议加强菜品的风味调配。"
            ])
        else:
            dish_summary = random.choice([
                f"{dish.DishName} 的评分较低，建议重新调整菜品配方和火候，提升顾客体验。",
                f"{dish.DishName} 在顾客中的评分较低，请根据顾客反馈改善口味和质感。"
            ])

        # 添加到菜品评分列表
        dish_ratings.append({
            'name': dish.DishName,
            'rating': round(avg_rating, 1) if avg_rating else 0,
            'review_count': review_count,
            'category': category,
            'dish_summary': dish_summary  # 菜品总结
        })

    # 定义档口总结话术
    high_rating_summaries = [
        "加油继续保持！您的档口和菜品的评分非常高，继续保持优秀的服务与品质！",
        "非常棒！档口和菜品的评分处于领先水平，继续维持高品质服务！",
        "优秀的表现！评分很高，继续保持这种水准，顾客会更加满意！"
    ]

    medium_rating_summaries = [
        "风味与火候有待提高，请继续改进以提升客户体验和整体满意度。",
        "您已经做得很好了！但风味和火候方面还有一些提升空间。",
        "整体不错，但有些菜品的风味或火候还需继续完善，确保一致性！"
    ]

    low_rating_summaries = [
        "情况不太乐观，要想办法改善一下了，考虑从菜品的质量和服务方面入手。",
        "您的档口和菜品评分较低，请尽快调整风味和质量，提升顾客满意度。",
        "需要加大改进力度，顾客对部分菜品的评价不高，务必从细节做起！"
    ]

    # 根据评分选择对应的总结话术
    if average_rating >= 4:
        summary = random.choice(high_rating_summaries)
    elif 3 <= average_rating < 4:
        summary = random.choice(medium_rating_summaries)
    else:
        summary = random.choice(low_rating_summaries)

    return render(request, 'ranking_sumup.html', {
        'dish_ratings': dish_ratings,  # 菜品评分数据
        'average_rating': round(average_rating, 1),  # 商家评分
        'summary': summary  # 商家评级总结
    })

def ranking_dishes(request):
    # 获取所有菜品评论数据，只筛选出 ObjType 为 2（菜品类型）的评论
    dish_reviews = Review.objects.filter(ObjType=2)  # 只获取菜品类型的评论

    # 使用 annotate 来计算每个菜品的平均评分和评论数
    db_dishes = dish_reviews.values('ObjID').annotate(
        average_rating=Avg('Rating'),  # 获取每个菜品的平均评分
        review_count=Count('id')  # 获取每个菜品的评论数量
    ).order_by('-average_rating')[:5]  # 按平均评分降序排序并取前5个菜品

    # 将获取的菜品数据与菜品、档口和食堂名称结合
    top_dishes = []
    for dish in db_dishes:
        # 获取对应菜品的名称
        dish_info = DishInfo.objects.get(id=dish['ObjID'])
        # 获取对应档口的名称
        stall_info = StallInfo.objects.get(id=dish_info.Stall.id)
        # 获取对应食堂的名称
        canteen_info = CanteenInfo.objects.get(id=stall_info.Canteen.id)

        top_dishes.append({
            'name': dish_info.DishName,  # 获取菜品名称
            'restaurant': canteen_info.CanteenName,  # 获取食堂名称
            'merchant': stall_info.StallName,  # 获取档口名称
            'reviews_count': dish['review_count'],  # 获取评论数量
            'rating': round(dish['average_rating'], 1) if dish['average_rating'] else 0  # 四舍五入保留一位小数
        })

    # 将数据传递到模板
    return render(request, 'ranking_dishes.html', {'top_dishes': top_dishes})

def ranking_restaurant(request):
    # 从 Review 表中获取餐厅评论数据
    restaurant_reviews = Review.objects.filter(ObjType=3)  # 只获取餐厅类型的评论

    # 使用 annotate 来计算每个餐厅的平均评分和评论数
    db_restaurants = restaurant_reviews.values('ObjID').annotate(
        average_rating=Avg('Rating'),  # 获取每个餐厅的平均评分
        review_count=Count('id')  # 获取每个餐厅的评论数量
    ).order_by('-average_rating')[:3]  # 按平均评分降序排序并取前3个餐厅

    # 将获取的餐厅数据与餐厅名称结合
    top_restaurants = []
    for restaurant in db_restaurants:
        canteen = CanteenInfo.objects.get(id=restaurant['ObjID'])  # 获取餐厅名称

        # 将餐厅数据（名称、评分、评论数）存储在列表中
        top_restaurants.append({
            'name': canteen.CanteenName,  # 从 CanteenInfo 获取餐厅名称
            'reviews_count': restaurant['review_count'],
            'rating': round(restaurant['average_rating'], 1) if restaurant['average_rating'] else 0  # 四舍五入保留一位小数
        })

    return render(request, 'ranking_restaurant.html', {'top_restaurants': top_restaurants})

def ranking_seller(request):
    # 获取所有档口评论数据，只筛选出 ObjType 为 1（档口类型）的评论
    stall_reviews = Review.objects.filter(ObjType=1)  # 只获取档口类型的评论

    # 使用 annotate 来计算每个档口的平均评分和评论数
    db_stalls = stall_reviews.values('ObjID').annotate(
        average_rating=Avg('Rating'),  # 获取每个档口的平均评分
        review_count=Count('id')  # 获取每个档口的评论数量
    ).order_by('-average_rating')[:5]  # 按平均评分降序排序并取前5个档口

    # 将获取的档口数据与档口和食堂名称结合
    top_rankings = []
    for stall in db_stalls:
        # 获取对应档口的名称
        stall_info = StallInfo.objects.get(id=stall['ObjID'])
        # 获取所属食堂的名称
        canteen_info = CanteenInfo.objects.get(id=stall_info.Canteen.id)

        top_rankings.append({
            'name': stall_info.StallName,  # 获取档口名称
            'location': canteen_info.CanteenName,  # 获取所属食堂名称
            'reviews_count': stall['review_count'],  # 获取评论数量
            'rating': round(stall['average_rating'], 1) if stall['average_rating'] else 0  # 四舍五入保留一位小数
        })

    return render(request, 'ranking_seller.html', {'top_rankings': top_rankings})






