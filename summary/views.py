from django.shortcuts import render
from summary.models import Ranking
from admin.models import CanteenInfo, StallInfo, DishInfo
from addReview.models import Review
from django.db.models import Avg, Count
from mine.models import UserInfo
import random  # 导入随机模块
from datetime import datetime, timedelta
from django.utils import timezone

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


'''def ranking_sumup(request):
    # 获取当前日期
    today = datetime.now()

    # 计算上一周的起始日期（上周一）
    last_week_start = today - timedelta(days=today.weekday() + 7)  # 上周一
    # 计算上一周的结束日期（上周日）
    last_week_end = last_week_start + timedelta(days=6)  # 上周日

    # 转换 naive datetime 为 aware datetime
    last_week_start = timezone.make_aware(last_week_start)
    last_week_end = timezone.make_aware(last_week_end)



    # 获取餐厅类型（ObjType=3）的评论
    restaurant_reviews = Review.objects.filter(ObjType=3, Timestamp__range=[last_week_start, last_week_end])

    # 用来存储每个餐厅的评分、评论数和总结
    restaurant_ratings = []

    # 获取所有餐厅ID并按ID分类
    restaurant_ids = restaurant_reviews.values('ObjID').distinct()

    if not restaurant_ids:
        print("No restaurant reviews found for distinct restaurant IDs.")

    for restaurant in restaurant_ids:
        # 获取该餐厅ID的所有评论
        reviews = restaurant_reviews.filter(ObjID=restaurant['ObjID'])

        # 计算餐厅的平均评分
        avg_rating = reviews.aggregate(Avg('Rating'))['Rating__avg'] or 0
        review_count = reviews.count()

        # 根据评分进行分类
        if avg_rating >= 4:
            category = '优秀'
        elif 3 <= avg_rating < 4:
            category = '合格'
        else:
            category = '不合格'

        # 根据餐厅评分生成个性化总结
        if avg_rating >= 4:
            restaurant_summary = f"餐厅的评分非常高，顾客评价极好，继续保持优质服务！"
        elif 3 <= avg_rating < 4:
            restaurant_summary = f"餐厅评分较好，但还有进一步提升的空间，请继续改善服务质量。"
        else:
            restaurant_summary = f"餐厅评分较低，需要从顾客反馈中改进质量和服务。"

        # 添加到餐厅评分列表
        restaurant_ratings.append({
            'restaurant_id': restaurant['ObjID'],
            'rating': round(avg_rating, 1),
            'review_count': review_count,
            'category': category,
            'restaurant_summary': restaurant_summary
        })

    # 商家评分总结逻辑
    if restaurant_ratings:
        avg_overall_rating = sum([r['rating'] for r in restaurant_ratings]) / len(restaurant_ratings)
        if avg_overall_rating >= 4:
            summary = "总体表现非常优秀，餐厅评价很高，请继续保持！"
        elif 3 <= avg_overall_rating < 4:
            summary = "餐厅评分良好，但仍有提升空间，请注意顾客反馈。"
        else:
            summary = "餐厅评分较低，需尽快提升整体服务和质量，关注顾客体验。"
    else:
        summary = "没有收到足够的评论，无法生成总结。"

    # 渲染结果
    return render(request, 'ranking_sumup.html', {
        'restaurant_ratings': restaurant_ratings,  # 餐厅评分数据
        'summary': summary  # 商家评级总结
    })'''

def get_dish_ratings():
    now = timezone.now()
    one_week_ago = now - timedelta(weeks=1)

    # 获取菜品类型的评论（ObjType=2）
    reviews = Review.objects.filter(ObjType=2, Timestamp__gte=one_week_ago, Timestamp__lte=now)

    if not reviews.exists():
        print("No dish reviews found in the last week.")
        return []

    dish_ratings = []
    dish_ids = reviews.values('ObjID').distinct()  # 获取所有不同的菜品ID

    # 获取每个菜品的评分数据
    for dish in dish_ids:
        dish_id = dish['ObjID']
        try:
            dish_info = DishInfo.objects.get(id=dish_id)
            dish_name = dish_info.DishName
            stall_name = dish_info.Stall.StallName  # 获取菜品所属档口名称
        except DishInfo.DoesNotExist:
            dish_name = "未知菜品"
            stall_name = "未知档口"

        # 获取该菜品的所有评论
        dish_reviews = reviews.filter(ObjID=dish_id)
        average_rating = dish_reviews.aggregate(Avg('Rating'))['Rating__avg'] or 0
        review_count = dish_reviews.count()

        if average_rating >= 4:
            category = '优秀'
        elif 3 <= average_rating < 4:
            category = '合格'
        else:
            category = '不合格'

        dish_summary = random.choice([
            f"{dish_name} 评分很高，顾客好评如潮，继续保持高质量！",
            f"{dish_name} 在顾客中反响不错，继续优化风味和品质！"
        ]) if average_rating >= 4 else "菜品评分较低，请改进菜品质量和口感。"

        dish_ratings.append({
            'dish_name': dish_name,
            'stall_name': stall_name,
            'rating': round(average_rating, 1),
            'category': category,
            'dish_summary': dish_summary
        })

    # 按评分排序，选取前五和倒数五个菜品
    sorted_dishes = sorted(dish_ratings, key=lambda x: x['rating'], reverse=True)
    top_five = sorted_dishes[:5]
    bottom_five = sorted_dishes[-5:]

    return top_five, bottom_five

def get_restaurant_ratings():
    # 获取当前时间和一周前的时间
    now = timezone.now()  # 当前时间
    one_week_ago = now - timedelta(weeks=1)  # 一周前的时间

    # 获取餐厅类型的评论（ObjType=3）
    reviews = Review.objects.filter(ObjType=3, Timestamp__gte=one_week_ago, Timestamp__lte=now)

    # 检查是否找到了评论
    if not reviews.exists():
        print("No restaurant reviews found in the last week.")
        return []

    # 用来存储每个餐厅的评分、评论数和分类
    restaurant_ratings = []

    # 获取餐厅的评分数据
    restaurant_ids = reviews.values('ObjID').distinct()  # 获取所有不同的餐厅ID

    for restaurant in restaurant_ids:
        restaurant_id = restaurant['ObjID']

        # 根据 ObjID 从 CanteenInfo 表中获取餐厅名称
        try:
            restaurant_info = CanteenInfo.objects.get(id=restaurant_id)
            restaurant_name = restaurant_info.CanteenName  # 获取餐厅名称
        except CanteenInfo.DoesNotExist:
            restaurant_name = "未知餐厅"  # 如果没有找到餐厅，默认名称为"未知餐厅"

        # 获取该餐厅的所有评论
        restaurant_reviews = reviews.filter(ObjID=restaurant_id)

        # 计算该餐厅的评分数据
        average_rating = restaurant_reviews.aggregate(Avg('Rating'))['Rating__avg'] or 0
        review_count = restaurant_reviews.count()

        # 根据评分进行分类
        if average_rating >= 4:
            category = '优秀'
        elif 3 <= average_rating < 4:
            category = '合格'
        else:
            category = '不合格'

        # 根据评分生成餐厅总结
        if average_rating >= 4:
            restaurant_summary = random.choice([
                "您的餐厅服务与菜品评分很高，请继续保持这一优异表现！",
                "顾客非常满意，继续维持高质量服务，您餐厅的评分非常优秀！"
            ])
        elif 3 <= average_rating < 4:
            restaurant_summary = random.choice([
                "餐厅服务和菜品评分不错，但仍有提升空间，请继续优化。",
                "风味和服务都有不错表现，建议进一步提升顾客满意度。"
            ])
        else:
            restaurant_summary = random.choice([
                "餐厅评分较低，请认真倾听顾客反馈并进行改善。",
                "需要改善餐厅的质量和服务，以提升顾客体验和满意度。"
            ])

        # 将数据添加到列表中
        restaurant_ratings.append({
            'restaurant_name': restaurant_name,  # 使用餐厅名称代替餐厅ID
            'review_count': review_count,
            'rating': round(average_rating, 1),  # 餐厅评分
            'category': category,
            'restaurant_summary': restaurant_summary  # 餐厅总结
        })

    return restaurant_ratings

def ranking_sumup(request):
    # 获取餐厅评分总结
    restaurant_ratings = get_restaurant_ratings()

    # 获取菜品评分总结
    top_five_dishes, bottom_five_dishes = get_dish_ratings()

    # 商家评分总结
    summary = "根据最新的评分数据，您的餐厅表现如下："

    # 菜品总结话术
    top_five_summary = "上周好评榜前五分别是："
    top_five = []
    for i, dish in enumerate(top_five_dishes, 1):
        top_five.append({
            'dish_name': dish['dish_name'],
            'stall_name': dish['stall_name'],
            'rating': dish['rating']
        })
        top_five_summary += f"{i}. {dish['dish_name']}，档口{dish['stall_name']}，评分：{dish['rating']}；"

    bottom_five_summary = "有待改进榜："
    bottom_five = []
    for i, dish in enumerate(bottom_five_dishes, 1):
        bottom_five.append({
            'dish_name': dish['dish_name'],
            'stall_name': dish['stall_name'],
            'rating': dish['rating']
        })
        bottom_five_summary += f"{i}. {dish['dish_name']}，档口{dish['stall_name']}，评分：{dish['rating']}；"

    # 返回渲染模板
    return render(request, 'ranking_sumup.html', {
        'restaurant_ratings': restaurant_ratings,  # 餐厅评分数据
        'summary': summary,  # 商家评分总结
        'top_five': top_five,  # 好评榜数据
        'bottom_five': bottom_five,  # 有待改进榜数据
        'top_five_summary': top_five_summary,  # 好评榜总结
        'bottom_five_summary': bottom_five_summary  # 有待改进榜总结
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






