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
from django.contrib import admin
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
from admin.views import admin
from admin.views import admin_register
from admin.views import admin_canteen_manage
from admin.views import admin_center
from admin.views import admin_message_center


urlpatterns = [
    path('index.html', index),
    path('mine.html', mine),
    path('add.html', addreview),
    path('search.html', search),
    path('login.html', login),
    path('admin.html', admin),
    path('manager.html', manager),
    path('my-comments.html', my_comments),
    path('feedback.html', feedback),
    path('ranking.html', rank),
    path('', index),
    path('admin.html', admin),
    path('admin_register.html', admin_register),
    path('admin_canteen_manage.html', admin_canteen_manage),
    path('admin_center.html', admin_center),
    path('admin_message_center.html', admin_message_center),
]
