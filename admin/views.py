from django.shortcuts import render
from django.db.models import Count
from .models import CanteenInfo, StallInfo, DishInfo
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse

# Create your views here.
def admin(request):
    # 用户和商家数量
    # 用户与商家数量
    # user_count = User.objects.filter(is_merchant=False).count()
    # merchant_count = User.objects.filter(is_merchant=True).count()

    # 获取所有食堂，统计每个食堂对应的档口数和菜品数
    canteens = CanteenInfo.objects.all()

    canteen_list = []
    for canteen in canteens:
        stall_count = StallInfo.objects.filter(Canteen=canteen).count()
        dish_count = DishInfo.objects.filter(Stall__Canteen=canteen).count()
        canteen_list.append({
            'name': canteen.CanteenName,
            'stall_count': stall_count,
            'dish_count': dish_count
        })

    return render(request, 'admin.html', {
        #'user_count': user_count,
        #'merchant_count': merchant_count,
        'canteen_list': canteen_list
    })
    #return render(request, 'admin.html')

def admin_register(request):
    """user_requests = User.objects.filter(status='pending', is_merchant=False)
    merchant_requests = User.objects.filter(status='pending', is_merchant=True)
    return render(request, 'admin_register.html', {
        'user_requests': user_requests,
        'merchant_requests': merchant_requests
    })"""
    return render(request, 'admin_register.html')

from django.shortcuts import render, redirect
from .models import CanteenInfo, StallInfo, DishInfo

def admin_canteen_manage(request):
    query_result = None
    has_searched = False
    no_result = False
    dish_deleted = False

    # 处理 POST 请求
    if request.method == 'POST':
        # 添加菜品
        if 'dish_name' in request.POST and 'canteen_name' in request.POST and 'stall_name' in request.POST:
            dish_name = request.POST.get('dish_name', '').strip()
            canteen_name = request.POST.get('canteen_name', '').strip()
            stall_name = request.POST.get('stall_name', '').strip()
            dish_description = request.POST.get('dish_description', '').strip()

            if not dish_name or not canteen_name or not stall_name:
                return redirect(reverse('admin_canteen_manage') + '?dish_add_failed=1')

            try:
                canteen = CanteenInfo.objects.filter(CanteenName=canteen_name).first()
                stall = StallInfo.objects.filter(StallName=stall_name, Canteen=canteen).first()

                if not canteen or not stall:
                    return redirect(reverse('admin_canteen_manage') + '?dish_add_failed=1')

                # 检查菜品是否重复
                if DishInfo.objects.filter(DishName=dish_name, Stall=stall).exists():
                    return redirect(reverse('admin_canteen_manage') + '?dish_add_failed=1')

                DishInfo.objects.create(DishName=dish_name, Stall=stall, Description=dish_description)
                return redirect(reverse('admin_canteen_manage') + '?dish_added=1')
            except:
                return redirect(reverse('admin_canteen_manage') + '?dish_add_failed=1')

        # 添加档口
        elif 'stall_name' in request.POST and 'canteen_id' in request.POST:
            stall_name = request.POST.get('stall_name', '').strip()
            canteen_id = request.POST.get('canteen_id', '').strip()

            if not stall_name or not canteen_id:
                return redirect(reverse('admin_canteen_manage') + '?stall_add_failed=1')

            try:
                canteen = CanteenInfo.objects.filter(id=canteen_id).first()

                if not canteen:
                    return redirect(reverse('admin_canteen_manage') + '?stall_add_failed=1')

                # 检查是否存在同名档口
                if StallInfo.objects.filter(StallName=stall_name, Canteen=canteen).exists():
                    return redirect(reverse('admin_canteen_manage') + '?stall_add_failed=1')

                StallInfo.objects.create(StallName=stall_name, Canteen=canteen)
                return redirect(reverse('admin_canteen_manage') + '?stall_added=1')
            except:
                return redirect(reverse('admin_canteen_manage') + '?stall_add_failed=1')

        # 添加食堂
        elif 'canteen_name' in request.POST:
            canteen_name = request.POST.get('canteen_name', '').strip()

            if not canteen_name:
                return redirect(reverse('admin_canteen_manage') + '?canteen_add_failed=1')

            try:
                if not CanteenInfo.objects.filter(CanteenName=canteen_name).exists():
                    CanteenInfo.objects.create(CanteenName=canteen_name)
                    return redirect(reverse('admin_canteen_manage') + '?canteen_added=1')
                else:
                    return redirect(reverse('admin_canteen_manage') + '?canteen_add_failed=1')
            except:
                return redirect(reverse('admin_canteen_manage') + '?canteen_add_failed=1')

        # 删除菜品
        elif 'delete_dish_name' in request.POST or 'delete_stall_name' in request.POST or 'delete_canteen_name' in request.POST:
            canteen_name = request.POST.get('delete_canteen_name', '').strip()
            stall_name = request.POST.get('delete_stall_name', '').strip()
            dish_name = request.POST.get('delete_dish_name', '').strip()

            try:
                if canteen_name and not stall_name and not dish_name:
                    # 只填了食堂，删除该食堂（会级联删除档口和菜品，假设模型 on_delete=CASCADE）
                    canteen = CanteenInfo.objects.get(CanteenName=canteen_name)
                    canteen.delete()
                    return redirect(reverse('admin_canteen_manage') + '?canteen_deleted=1')

                elif canteen_name and stall_name and not dish_name:
                    # 填了食堂和档口，删除该档口（会级联删除菜品）
                    canteen = CanteenInfo.objects.get(CanteenName=canteen_name)
                    stall = StallInfo.objects.get(StallName=stall_name, Canteen=canteen)
                    stall.delete()
                    return redirect(reverse('admin_canteen_manage') + '?stall_deleted=1')

                elif canteen_name and stall_name and dish_name:
                    # 填了食堂、档口和菜品，删除该菜品
                    canteen = CanteenInfo.objects.get(CanteenName=canteen_name)
                    stall = StallInfo.objects.get(StallName=stall_name, Canteen=canteen)
                    dish = DishInfo.objects.get(DishName=dish_name, Stall=stall)
                    dish.delete()
                    return redirect(reverse('admin_canteen_manage') + '?dish_deleted=1')

                else:
                    # 参数不完整或不符合预期
                    return redirect(reverse('admin_canteen_manage') + '?delete_failed=1')
            except (CanteenInfo.DoesNotExist, StallInfo.DoesNotExist, DishInfo.DoesNotExist):
                return redirect(reverse('admin_canteen_manage') + '?delete_failed=1')

    # 处理 GET 查询
    if request.method == 'GET':
        q_canteen = request.GET.get('canteen', '').strip()
        q_stall = request.GET.get('stall', '').strip()
        q_dish = request.GET.get('dish', '').strip()

        if q_canteen or q_stall or q_dish:
            has_searched = True

            canteen = CanteenInfo.objects.filter(CanteenName=q_canteen).first()
            if canteen:
                stall = StallInfo.objects.filter(StallName=q_stall, Canteen=canteen).first() if q_stall else None
                if q_stall and not stall:
                    no_result = True
                else:
                    if stall:
                        dish = DishInfo.objects.filter(DishName=q_dish, Stall=stall).first() if q_dish else None
                        if q_dish and not dish:
                            no_result = True
                        else:
                            query_result = {
                                'canteen': canteen.CanteenName,
                                'stall': stall.StallName if stall else '(未指定档口)',
                                'dish': dish.DishName if dish else '',
                                'description': dish.Description if dish else '',
                            }
                    else:
                        # 只查询食堂时
                        query_result = {
                            'canteen': canteen.CanteenName,
                            'stall': '',
                            'dish': '',
                            'description': '',
                        }
            else:
                no_result = True

    # 页面加载数据
    canteens = CanteenInfo.objects.all()
    stalls = StallInfo.objects.all()

    return render(request, 'admin_canteen_manage.html', {
        'canteens': canteens,
        'stalls': stalls,
        'query_result': query_result,
        'no_result': no_result,
        'has_searched': has_searched,
        'dish_deleted': dish_deleted
    })


def admin_center(request):
    return render(request, 'admin_center.html')

def admin_message_center(request):
    return render(request, 'admin_message_center.html')
