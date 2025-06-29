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
def generate_summary(is_positive=True):
    if is_positive:
        positive_summaries = [
            "这些菜品普遍符合大众口味，价格合理，且服务态度良好。顾客普遍评价为“美味”、“物超所值”。",
            "顾客反馈非常好，菜品口味丰富，价格实惠，服务态度也让人满意。",
            "这些菜品深受顾客喜爱，具有独特的风味，顾客普遍给予好评。",
            "菜品的口感和味道都很受欢迎，价格合理，顾客纷纷表示愿意再次光顾。"
        ]
        return random.choice(positive_summaries)
    else:
        negative_summaries = [
            "这些菜品的评分较低，建议改善口感、提供更好的服务，或调整价格策略以吸引顾客。",
            "顾客对这些菜品的评价不太理想，需进一步提升菜品质量和顾客体验。",
            "菜品的味道偏淡或口感欠佳，顾客反馈较为冷淡，建议改进。",
            "这些菜品的评分较低，客户提出了多方面的改进建议，需引起重视。"
        ]
        return random.choice(negative_summaries)

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
    reviews = Review.objects.filter(ObjType=3, Timestamp__gte=one_week_ago, Timestamp__lte=now)

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
    bottom_five = sorted_dishes[-5:][::-1]

    return top_five, bottom_five

def get_restaurant_ratings():
    # 获取当前时间和一周前的时间
    now = timezone.now()  # 当前时间
    one_week_ago = now - timedelta(weeks=1)  # 一周前的时间

    # 获取餐厅类型的评论（ObjType=3）
    reviews = Review.objects.filter(ObjType=1, Timestamp__gte=one_week_ago, Timestamp__lte=now)

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
                "餐厅服务与菜品评分非常高，顾客反响热烈，继续保持这份卓越的表现，定能吸引更多回头客！",
                "顾客对餐厅的评价非常好，服务和菜品都非常到位，继续发扬光大，保持高标准！",
                "餐厅在顾客心中已经建立了很强的好感，维持这种优质的体验，定能长期稳定客户群。",
                "评分非常高，餐厅表现优秀，建议加强创新，保持并提升当前服务水平！",
                "顾客非常满意，您的餐厅表现出色，继续提供这一高质量的餐饮体验，赢得更多忠实顾客！"
            ])
        elif 3 <= average_rating < 4:
            restaurant_summary = random.choice([
                "餐厅服务和菜品表现不错，顾客总体满意，但仍有一些地方可以做得更好，请继续提升！",
                "风味和服务表现稳定，餐厅已具备良好的基础，进一步优化顾客细节体验会让评分更高！",
                "评分良好，餐厅在很多方面都表现不错，但细节的优化和创新会帮助您获得更多好评。",
                "餐厅整体表现不错，但仍有提升空间，建议优化菜品口味和服务细节，争取更高评分。",
                "餐厅有不错的基础，顾客反馈较好，进一步提升餐饮质量和服务体验，能带来更多顾客满意！"
            ])
        else:
            restaurant_summary = random.choice([
                "餐厅评分偏低，顾客反馈存在不满，建议重视顾客评价，提升服务质量和菜品口味。",
                "餐厅评分较低，需要积极听取顾客意见并立即改进，改善菜品和服务，才能提高顾客满意度。",
                "顾客对餐厅的整体评分较低，急需提升菜品质量和服务水平，才能赢得更多顾客的认可。",
                "餐厅评分较低，请务必关注顾客反馈，优化菜品和服务，提升餐厅整体水平。",
                "餐厅评分较低，需要改善菜品口味和提升服务质量，以便更好地满足顾客需求，增加回头客。"
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

    # 好评榜总结话术
    top_five_summary = generate_summary(is_positive=True)

    top_five = []
    for i, dish in enumerate(top_five_dishes, 1):
        top_five.append({
            'dish_name': dish['dish_name'],
            'stall_name': dish['stall_name'],
            'rating': dish['rating']
        })

    # 差评榜总结话术
    bottom_five_summary = generate_summary(is_positive=False)

    bottom_five = []
    for i, dish in enumerate(bottom_five_dishes, 1):
        bottom_five.append({
            'dish_name': dish['dish_name'],
            'stall_name': dish['stall_name'],
            'rating': dish['rating']
        })

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
    dish_reviews = Review.objects.filter(ObjType=3)  # 只获取菜品类型的评论

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
    restaurant_reviews = Review.objects.filter(ObjType=1)  # 只获取餐厅类型的评论

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


from django.db.models import Avg, Count


def ranking_seller(request):
    # 获取所有档口评论数据，只筛选出 ObjType 为 2（档口类型）的评论
    stall_reviews = Review.objects.filter(ObjType=2)  # 只获取档口类型的评论

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

        # 获取该档口的所有菜品
        dishes = DishInfo.objects.filter(Stall=stall_info)

        # 对每个菜品计算平均评分并选择评分最高的菜品
        best_dish = None
        highest_rating = 0

        for dish in dishes:
            # 获取该菜品的平均评分
            dish_avg_rating = Review.objects.filter(ObjID=dish.id, ObjType=3).aggregate(Avg('Rating'))['Rating__avg']

            if dish_avg_rating and dish_avg_rating > highest_rating:
                best_dish = dish
                highest_rating = dish_avg_rating

        # 如果找到了评分最高的菜品，则取该菜品名称，否则标记为"无特色菜"
        specialty = best_dish.DishName if best_dish else '无特色菜'

        top_rankings.append({
            'name': stall_info.StallName,  # 获取档口名称
            'location': canteen_info.CanteenName,  # 获取所属食堂名称
            'reviews_count': stall['review_count'],  # 获取评论数量
            'rating': round(stall['average_rating'], 1) if stall['average_rating'] else 0,  # 四舍五入保留一位小数
            'specialties': specialty  # 获取特色菜名称
        })

    return render(request, 'ranking_seller.html', {'top_rankings': top_rankings})







