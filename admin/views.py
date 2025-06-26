from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Count
from admin.models import CanteenInfo, StallInfo, DishInfo
from mine.models import UserInfo, AuthMessage
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

# Create your views here.
def admin(request):
    # 用户和商家数量
    user_count = UserInfo.objects.filter(UserType=1).count()
    merchant_count = UserInfo.objects.filter(UserType=2).count()

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
        'user_count': user_count,
        'merchant_count': merchant_count,
        'canteen_list': canteen_list
    })

def admin_register(request):
    # 处理“同意”或“驳回”按钮
    if request.method == 'POST':
        action = request.POST.get('action')
        auth_id = request.POST.get('auth_id')
        auth = get_object_or_404(AuthMessage, id=auth_id, Validity=1)

        if action == 'approve':
            try:
                user = UserInfo.objects.get(id=auth.UserID)
                user.StallID = auth.StallID
                user.save()
                auth.Validity = 0
                auth.save()
            except UserInfo.DoesNotExist:
                pass

        elif action == 'reject':
            auth.Validity = 0
            auth.save()

        return redirect(reverse('admin_register'))

    # GET 请求：展示注册认证请求
    auth_requests = AuthMessage.objects.filter(Validity=1)
    auth_with_stall_name = []
    for auth in auth_requests:
        try:
            stall = StallInfo.objects.get(id=auth.StallID)
            stall_name = stall.StallName
        except StallInfo.DoesNotExist:
            stall_name = "（档口不存在）"
        auth_with_stall_name.append({
            'id': auth.id,
            'Username': auth.Username,
            'StallID': auth.StallID,
            'Describe': auth.Describe,
            'StallName': stall_name,
        })

    return render(request, 'admin_register.html', {
        'auth_requests': auth_with_stall_name,
    })


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
                print("填入为空")
                return redirect(reverse('admin_canteen_manage') + '?dish_add_failed=1')

            try:
                canteen = CanteenInfo.objects.filter(CanteenName=canteen_name).first()
                stall = StallInfo.objects.filter(StallName=stall_name, Canteen=canteen).first()

                if not canteen or not stall:
                    print("没有食堂或档口")
                    return redirect(reverse('admin_canteen_manage') + '?dish_add_failed=1')

                # 检查菜品是否重复
                if DishInfo.objects.filter(DishName=dish_name, Stall=stall).exists():
                    print("菜品重复")
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
    stalls = StallInfo.objects.select_related('Canteen').all()
    dishes = DishInfo.objects.select_related('Stall').all()

    return render(request, 'admin_canteen_manage.html', {
        'canteens': canteens,
        'stalls': stalls,
        'dishes': dishes,
        'query_result': query_result,
        'no_result': no_result,
        'has_searched': has_searched,
        'dish_deleted': dish_deleted
    })


def admin_center(request):
    # ******************
    # 1. 处理修改密码请求
    # ******************
    pwd_changed = False
    pwd_error = ''
    if request.method == 'POST' and 'change_pwd' in request.POST:
        admin_id = request.POST.get('admin_id')
        old_pwd = request.POST.get('old_password', '').strip()
        new_pwd1 = request.POST.get('new_password1', '').strip()
        new_pwd2 = request.POST.get('new_password2', '').strip()

        admin = get_object_or_404(UserInfo, id=admin_id, UserType=3)
        # 校验旧密码是否一致
        if admin.Password != old_pwd:
            pwd_error = '旧密码不正确'
        elif new_pwd1 == old_pwd :
            pwd_error = '新密码输入与旧密码一致'
        # 校验两次新密码
        elif not new_pwd1 or new_pwd1 != new_pwd2:
            pwd_error = '两次新密码输入不一致或为空'
        else:
            # 全部合法，更新密码
            admin.Password = new_pwd1
            admin.save()
            pwd_changed = True
            # 重定向避免 F5 重复提交
            return redirect(reverse('admin_center') + '?pwd_changed=1')

    # 从 GET 参数读取重定向后的提示
    if request.GET.get('pwd_changed') == '1':
        pwd_changed = True

    # ******************
    # 2. 获取所有管理员账号列表
    # ******************
    admins = UserInfo.objects.filter(UserType=3)

    return render(request, 'admin_center.html', {
        'admins': admins,
        'pwd_changed': pwd_changed,
        'pwd_error': pwd_error,
    })

def admin_message_center(request):
    return render(request, 'admin_message_center.html')
