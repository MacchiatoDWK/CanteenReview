from django.shortcuts import render

# Create your views here.


def mine(request):
    return render(request, 'mine.html')


def login(request):
    if request.method == "GET":
        return render(request, 'login.html', {"type": True})
    else:
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        if user is not None and pwd is not None:

            return render(request, 'login.html', {"error": user, "type": True})
        else:
            reg_user = request.POST.get('reg_user')
            reg_pwd = request.POST.get('reg_pwd')
            reg_pwd_again = request.POST.get('reg_pwd_again')
            return render(request, 'login.html', {"error": reg_user, "type": False})


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