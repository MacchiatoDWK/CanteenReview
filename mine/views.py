from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from mine import models
import random
# Create your views here.


def mine(request):
    if request.method == "GET":
        return render(request, 'mine.html')
    else:
        response = render(request, 'mine.html')
        response.delete_cookie('username', path='/')
        response.delete_cookie('usertype', path='/')
        return response


def login(request):
    if request.method == "GET":
        return render(request, 'login.html', {"type": True})
    else:
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        if user is not None and pwd is not None:
            reg_temp = models.UserInfo.objects.filter(Username=user).first()
            if reg_temp is not None:
                if reg_temp.Password == pwd:
                    response = redirect('mine.html')
                    response.set_cookie('userid', str(reg_temp.id), path='/', max_age=60 * 60 * 24 * 3)
                    response.set_cookie('username', user, path='/', max_age=60*60*24*3)
                    response.set_cookie('usertype', str(reg_temp.UserType), path='/', max_age=60*60*24*3)
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
                reg_temp = models.UserInfo.objects.filter(Username=reg_user)
                if not reg_temp:
                    if len(reg_user) < 20 and len(reg_pwd) < 20:
                        if reg_type == "1":
                            models.UserInfo.objects.create(Username=reg_user, Password=reg_pwd, UserType=1)
                        else:
                            models.UserInfo.objects.create(Username=reg_user, Password=reg_pwd, UserType=2)
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


def admin(request):
    return render(request, 'admin.html')


def manager(request):
    return render(request, 'manager.html')


def my_comments(request):
    return render(request, 'my-comments.html')


def feedback(request):
    return render(request, 'feedback.html')


def rank(request):
    return render(request, 'ranking.html')