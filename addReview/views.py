from django.shortcuts import render, redirect


# Create your views here.


def addreview(request):
    return render(request, 'add.html')


