from django.shortcuts import render



# Create your views here.
def admin(request):
    # 用户和商家数量
    # 模拟用户和商家数量
    user_count = 1240
    merchant_count = 87

    # 模拟食堂数据列表
    canteen_list = [
        {'name': '🍱 风味餐厅', 'stall_count': 8, 'dish_count': 64},
        {'name': '🍜 美食园', 'stall_count': 6, 'dish_count': 50},
        {'name': '🥢 天天食堂', 'stall_count': 5, 'dish_count': 35},
        {'name': '🕌 清真食堂', 'stall_count': 3, 'dish_count': 20},
        {'name': '🏅 奥运餐厅', 'stall_count': 7, 'dish_count': 45},
        {'name': '☕ 天天咖啡馆', 'stall_count': 4, 'dish_count': 30},
    ]

    return render(request, 'admin.html', {
        'user_count': user_count,
        'merchant_count': merchant_count,
        'canteen_list': canteen_list
    })

    """user_count = User.objects.filter(is_merchant=False).count()
    merchant_count = User.objects.filter(is_merchant=True).count()

    # 所有食堂统计信息
    canteens = Canteen.objects.all()
    canteen_stats = []
    for canteen in canteens:
        stalls = Stall.objects.filter(canteen=canteen)
        stall_count = stalls.count()
        dish_count = Dish.objects.filter(stall__in=stalls).count()
        canteen_stats.append({
            'name': canteen.name,
            'stall_count': stall_count,
            'dish_count': dish_count
        })

    return render(request, 'admin.html', {
        'user_count': user_count,
        'merchant_count': merchant_count,
        'canteen_stats': canteen_stats
    })"""
    #return render(request, 'admin.html')

def admin_register(request):
    """user_requests = User.objects.filter(status='pending', is_merchant=False)
    merchant_requests = User.objects.filter(status='pending', is_merchant=True)
    return render(request, 'admin_register.html', {
        'user_requests': user_requests,
        'merchant_requests': merchant_requests
    })"""
    return render(request, 'admin_register.html')

def admin_canteen_manage(request):
    """if request.method == "POST":
        if 'canteen_name' in request.POST:
            # 新增食堂逻辑
            ...
        elif 'stall_name' in request.POST:
            # 新增档口逻辑
            ...
        elif 'dish_name' in request.POST:
            # 新增菜品逻辑
            ..."""
    return render(request, 'admin_canteen_manage.html')

def admin_center(request):
    return render(request, 'admin_center.html')

def admin_message_center(request):
    return render(request, 'admin_message_center.html')