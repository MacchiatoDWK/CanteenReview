from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from mine import models as MM
from admin import models as AM
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
        return render(request, 'login.html', {"type": True})
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
                    return render(request, 'login.html', {"error": "用户名或密码不正确", "type": True})
            else:
                return render(request, 'login.html', {"error": "用户名或密码不正确", "type": True})
        else:
            code_input = request.POST.get('reg_code')
            code_real = request.session.get('email_code')
            if code_input != code_real:
                return render(request, 'login.html', {"error": "验证码不正确", "type": False})

            reg_user = request.POST.get('reg_user')
            reg_pwd = request.POST.get('reg_pwd')
            reg_pwd_again = request.POST.get('reg_pwd_again')
            reg_type = request.POST.get('reg_type')
            if reg_pwd == reg_pwd_again:
                reg_temp = MM.UserInfo.objects.filter(Username=reg_user)
                if not reg_temp:
                    if len(reg_user) < 20 and len(reg_pwd) < 20:
                        if reg_type == "1":
                            MM.UserInfo.objects.create(Username=reg_user, Password=reg_pwd, UserType=1)
                        else:
                            MM.UserInfo.objects.create(Username=reg_user, Password=reg_pwd, UserType=2)
                        return render(request, 'login.html', {"type": True})
                    else:
                        return render(request, 'login.html', {"error": "注册失败", "type": False})
                else:
                    return render(request, 'login.html', {"error": "该邮箱已注册", "type": False})
            else:
                return render(request, 'login.html', {"error": "密码与确认密码不一致", "type": False})


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
    if userid is None:
        return render(request, 'index.html')
    else:
        stallid = MM.UserInfo.objects.filter(id=userid).first().StallID
    if stallid is None:
        manager_temp = MM.AuthMessage.objects.filter(UserID=userid)
        if manager_temp:
            manager_temp = MM.AuthMessage.objects.filter(UserID=userid, Validity=1)
            if manager_temp:
                return render(request, 'auth.html', {
                    'success': True,
                    'msg': '审核尚未通过',
                    'back': True
                })
            else:
                return render(request, 'auth.html', {
                    'success': True,
                    'msg': '申请未审核通过，可重新申请',
                    'back': False
                })
        else:
            return render(request, 'auth.html')
    return render(request, 'manager.html')


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
    return render(request, 'my-comments.html')


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
