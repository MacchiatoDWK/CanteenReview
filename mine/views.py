from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from mine import models as MM
from admin import models as AM
from addReview import models as AR
import random


# Create your views here.


def mine(request):
    if request.method == "GET":
        return render(request, 'mine.html')
    else:
        response = render(request, 'mine.html')
        response.delete_cookie('username', path='/')
        response.delete_cookie('usertype', path='/')
        response.delete_cookie('userid', path='/')
        return response


def login(request):
    if request.method == "GET":
        return render(request, 'login.html', {"type": 1})
    else:
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        if user is not None and pwd is not None:
            reg_temp = MM.UserInfo.objects.filter(Username=user).first()
            if reg_temp is not None:
                if reg_temp.Password == pwd:
                    response = redirect('mine.html')
                    response.set_cookie('userid', str(reg_temp.id), path='/', max_age=60 * 60 * 24 * 3)
                    response.set_cookie('username', user, path='/', max_age=60 * 60 * 24 * 3)
                    response.set_cookie('usertype', str(reg_temp.UserType), path='/', max_age=60 * 60 * 24 * 3)
                    return response
                else:
                    return render(request, 'login.html', {"error": "用户名或密码不正确", "type": 1})
            else:
                return render(request, 'login.html', {"error": "用户名或密码不正确", "type": 1})
        else:
            reg_user = request.POST.get('reg_user')
            reg_pwd = request.POST.get('reg_pwd')
            reg_pwd_again = request.POST.get('reg_pwd_again')
            reg_type = request.POST.get('reg_type')
            if reg_user is not None and reg_pwd is not None and reg_pwd_again is not None:
                code_input = request.POST.get('reg_code')
                code_real = request.session.get('email_code')
                if code_input != code_real:
                    return render(request, 'login.html', {"error": "验证码不正确", "type": 2})

                if reg_pwd == reg_pwd_again:
                    reg_temp = MM.UserInfo.objects.filter(Username=reg_user)
                    if not reg_temp:
                        if len(reg_user) < 40 and len(reg_pwd) < 20:
                            if reg_type == "1":
                                MM.UserInfo.objects.create(Username=reg_user, Password=reg_pwd, UserType=1)
                            else:
                                MM.UserInfo.objects.create(Username=reg_user, Password=reg_pwd, UserType=2)
                            del request.session['email_code']
                            return render(request, 'login.html', {"type": 1,
                                                                                        "success": True,
                                                                                        "msg": "注册成功"})
                        else:
                            return render(request, 'login.html', {"error": "注册失败", "type": 2})
                    else:
                        return render(request, 'login.html', {"error": "该邮箱已注册", "type": 2})
                else:
                    return render(request, 'login.html', {"error": "密码与确认密码不一致", "type": 2})
            else:
                reset_user = request.POST.get('reset_user')
                reset_pwd = request.POST.get('reset_pwd')
                code_input = request.POST.get('reset_code')
                code_real = request.session.get('email_code')
                if code_input != code_real:
                    return render(request, 'login.html', {"error": "验证码不正确", "type": 3})
                else:
                    reset_temp = MM.UserInfo.objects.filter(Username=reset_user)
                    if reset_temp is not None:
                        reset_temp.update(Password = reset_pwd)
                        del request.session['email_code']
                        return render(request, 'login.html', {"type": 1,
                                                                                   "success": True,
                                                                                   "msg": "密码重置成功"})
                    else:
                        return render(request, 'login.html', {"error": "没有该用户", "type": 3})


def send_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return JsonResponse({'success': False, 'msg': '邮箱不能为空'})

        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        send_mail(
            subject='注册验证码',
            message=f'您的验证码是：{code}，有效期5分钟。',
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        # 存入 session
        request.session['email_code'] = code
        request.session['email_target'] = email
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'msg': '仅支持POST请求'})


def manager(request):
    userid = request.COOKIES.get('userid')
    usertype = request.COOKIES.get('usertype')
    username = request.COOKIES.get('username')
    
    print(f"manager视图 - userid: {userid}, usertype: {usertype}, username: {username}")
    
    if userid is None:
        print("用户未登录，重定向到首页")
        return render(request, 'index.html')
    
    # 确保用户是商家
    if usertype != '2':
        print(f"用户类型不是商家: {usertype}")
        return render(request, 'index.html')
    
    try:
        user = MM.UserInfo.objects.get(id=userid)
        stallid = user.StallID
        print(f"查询到用户 {userid} 的档口ID: {stallid}")
    except Exception as e:
        print(f"查询用户信息出错: {str(e)}")
        stallid = None
    
    if stallid is None:
        manager_temp = MM.AuthMessage.objects.filter(UserID=userid)
        if manager_temp:
            manager_temp = MM.AuthMessage.objects.filter(UserID=userid, Validity=1)
            if manager_temp:
                print("用户有待审核的认证申请")
                return render(request, 'auth.html', {
                    'success': True,
                    'msg': '审核尚未通过',
                    'back': True
                })
            else:
                print("用户的认证申请未通过")
                return render(request, 'auth.html', {
                    'success': True,
                    'msg': '申请未审核通过，可重新申请',
                    'back': False
                })
        else:
            print("用户未提交认证申请")
            return render(request, 'auth.html')
    
    print("用户已绑定档口，显示商家管理页面")
    # 确保Cookie正确设置
    response = render(request, 'manager.html')
    
    # 重新设置Cookie，确保它们存在且有效
    if not request.COOKIES.get('userid'):
        response.set_cookie('userid', str(userid), path='/', max_age=60 * 60 * 24 * 3)
    if not request.COOKIES.get('usertype'):
        response.set_cookie('usertype', str(usertype), path='/', max_age=60 * 60 * 24 * 3)
    if not request.COOKIES.get('username'):
        response.set_cookie('username', username, path='/', max_age=60 * 60 * 24 * 3)
    
    return response


def get_stalls(request):
    canteen_id = request.GET.get('canteen_id')
    stalls = AM.StallInfo.objects.filter(Canteen=canteen_id).values('id', 'StallName')
    return JsonResponse({'stalls': list(stalls)})


def get_canteens(request):
    canteens = AM.CanteenInfo.objects.all().values('id', 'CanteenName')
    return JsonResponse({'canteens': list(canteens)})


def get_dishes(request):
    stall_id = request.GET.get('stall_id')
    dishes = AM.DishInfo.objects.filter(Stall_id=stall_id).values('id', 'DishName')
    return JsonResponse({'dishes': list(dishes)})


def submit_auth(request):
    userid = request.COOKIES.get('userid')
    username = request.COOKIES.get('username')
    stall = request.POST.get('stall')
    describe = request.POST.get('describe')
    MM.AuthMessage.objects.create(UserID=userid, Username=username, StallID=stall, Describe=describe, Validity=1)
    return render(request, 'auth.html', {
        'success': True,
        'msg': '提交成功',
        'back': True
    })


def submit_feedback(request):
    userid = request.COOKIES.get('userid')
    username = request.COOKIES.get('username')
    canteen = request.POST.get('canteen')
    stall = request.POST.get('stall')
    dish = request.POST.get('dish')
    describe = request.POST.get('describe')
    if canteen == "" and stall is None and dish is None:
        MM.FeedbackMessage.objects.create(UserID=userid, Username=username, Describe=describe, Validity=1)
    else:
        if stall == "" and dish is None:
            MM.FeedbackMessage.objects.create(UserID=userid, Username=username, CanteenID=canteen, Describe=describe,
                                              Validity=1)
        else:
            if dish == "":
                MM.FeedbackMessage.objects.create(UserID=userid, Username=username, CanteenID=canteen, StallID=stall,
                                                  Describe=describe, Validity=1)
            else:
                MM.FeedbackMessage.objects.create(UserID=userid,
                                                  Username=username,
                                                  CanteenID=canteen,
                                                  StallID=stall,
                                                  DishID=dish,
                                                  Describe=describe,
                                                  Validity=1)
    return render(request, 'feedback.html', {
        'success': True,
        'msg': '提交成功',
        'back': True
    })


def my_comments(request):
    userid = request.COOKIES.get('userid')
    usertype = request.COOKIES.get('usertype')
    username = request.COOKIES.get('username')
    if userid is not None and usertype is not None and username is not None:
        return render(request, 'my-comments.html')
    else:
        return render(request, 'my-comments.html', {
            'success': True,
            'msg': '请先登录',
            'back': True
        })

def get_my_comments(request):
    page = int(request.GET.get('page', 1))
    page_size = 10

    userid = request.COOKIES.get('userid')

    reviews = AR.Review.objects.filter(UserID=userid).order_by('-Timestamp')
    paginator = Paginator(reviews, page_size)
    page_obj = paginator.get_page(page)

    comment_data = []

    for review in page_obj:
        # 获取被评论对象名称
        if review.ObjType == 1:
            try:
                canteenName = AM.CanteenInfo.objects.get(id=review.ObjID).CanteenName
                stallName = ""
                dishName = ""
            except:
                canteenName = "已删除食堂"
                stallName = ""
                dishName = ""
        elif review.ObjType == 2:
            try:
                canteenid = AM.StallInfo.objects.get(id=review.ObjID).Canteen_id
                canteenName = AM.CanteenInfo.objects.get(id=canteenid).CanteenName
                stallName = AM.StallInfo.objects.get(id=review.ObjID).StallName
                dishName = ""
            except:
                canteenName = "已删除食堂"
                stallName = "已删除档口"
                dishName = ""
        elif review.ObjType == 3:
            try:
                stallid = AM.DishInfo.objects.get(id=review.ObjID).Stall_id
                stallName = AM.StallInfo.objects.get(id=stallid).StallName
                canteenid = AM.StallInfo.objects.get(id=stallid).Canteen_id
                canteenName = AM.CanteenInfo.objects.get(id=canteenid).CanteenName
                dishName = AM.DishInfo.objects.get(id=review.ObjID).DishName
            except:
                canteenName = "已删除食堂"
                stallName = "已删除档口"
                dishName = "已删除菜品"
        else:
            canteenName = ""
            stallName = ""
            dishName = ""

        # 获取图片
        images = AR.Image.objects.filter(ReviewID=review.id)
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

def delete_review(request):
    if request.method == 'POST':
        review_id = int(request.GET.get('id', 1))
        userid = int(request.COOKIES.get('userid'))
        try:
            review = AR.Review.objects.get(id=review_id)
            if userid != review.UserID:
                return JsonResponse({'success': False, 'msg': '无权限删除'})
            AR.Image.objects.filter(ReviewID=review_id).delete()
            AR.Review.objects.get(id=review_id).delete()
            return JsonResponse({'success': True})
        except AR.Review.DoesNotExist:
            return JsonResponse({'success': False, 'msg': '评论不存在'})
    return JsonResponse({'success': False, 'msg': '仅支持 POST'})

def feedback(request):
    userid = request.COOKIES.get('userid')
    usertype = request.COOKIES.get('usertype')
    username = request.COOKIES.get('username')
    if userid is not None and usertype is not None and username is not None:
        feedback_temp = MM.FeedbackMessage.objects.filter(UserID=userid)
        if feedback_temp:
            feedback_temp = MM.FeedbackMessage.objects.filter(UserID=userid, Validity=1)
            if feedback_temp.count() >= 3:
                return render(request, 'feedback.html', {
                    'success': True,
                    'msg': '你的反馈过多，请等待反馈核实',
                    'back': True
                })
            else:
                return render(request, 'feedback.html')
        else:
            return render(request, 'feedback.html')
    else:
        return render(request, 'feedback.html', {
            'success': True,
            'msg': '请先登录',
            'back': True
        })

def rank(request):
    return render(request, 'ranking.html')
