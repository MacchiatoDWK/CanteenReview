"""CanteenReview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.shortcuts import HttpResponse
from mainPage.views import index
from mine.views import mine
from addReview.views import addreview
from search.views import search
from mine.views import login
from mine.views import manager
from mine.views import my_comments
from mine.views import feedback
from mine.views import rank
from admin import views

from mine.views import send_code


urlpatterns = [
    path('index.html', index),
    path('mine.html', mine),
    path('add.html', addreview),
    path('search.html', search),
    path('login.html', login),
    #path('admin.html', admin),
    path('manager.html', manager),
    path('my-comments.html', my_comments),
    path('feedback.html', feedback),
    path('ranking.html', rank),
    path('send_code/', send_code, name='send_code'),
    path('', index),
    #path('admin.html', admin),
    #path('admin_register.html', admin_register),
    #path('admin_canteen_manage.html', admin_canteen_manage),
    #path('admin_center.html', admin_center),
    #path('admin_message_center.html', admin_message_center),
    path('admin/', views.admin, name='admin'),
    path('center/', views.admin_center, name='admin_center'),
    path('messages/', views.admin_message_center, name='admin_message_center'),
    path('register/', views.admin_register, name='admin_register'),
    path('canteen/', views.admin_canteen_manage, name='admin_canteen_manage'),
]
