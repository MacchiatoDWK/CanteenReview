from django.shortcuts import render

# Create your views here.


def mine(request):
    return render(request, 'mine.html')


def login(request):
    return render(request, 'login.html')


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