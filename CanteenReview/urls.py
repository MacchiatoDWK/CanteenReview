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
from mainPage.views import index, get_comments
from merchant.views import get_stall_comments, get_rating_distribution, get_dish_avg_scores
from mine.views import mine, get_stalls, get_canteens, submit_auth, get_dishes, submit_feedback, get_my_comments, \
    delete_review
from addReview.views import addreview, submit_comment
from search.views import search
from search.views import detail
from mine.views import login
from mine.views import manager
from mine.views import my_comments
from mine.views import feedback
from mine.views import rank
from mine.views import send_code
from admin import views
from django.conf import settings
from django.conf.urls.static import static
from summary.views import ranking
from summary.views import ranking_sumup
from summary.views import ranking_dishes
from summary.views import ranking_restaurant
from summary.views import ranking_seller


urlpatterns = [
    path('index.html', index),
    path('mine.html', mine),
    path('add.html', addreview),
    path('search.html', search, name='search'),
    path('detail/<int:item_id>/', detail, name='detail'),
    path('login.html', login),
    path('manager.html', manager),
    path('my-comments.html', my_comments),
    path('feedback.html', feedback),
    path('ranking.html', rank),
    path('send_code/', send_code, name='send_code'),
    path('', index),
    path('admin/', views.admin, name='admin'),
    path('center/', views.admin_center, name='admin_center'),
    path('messages/', views.admin_message_center, name='admin_message_center'),
    path('register/', views.admin_register, name='admin_register'),
    path('canteen/', views.admin_canteen_manage, name='admin_canteen_manage'),
    path('get_canteens/', get_canteens, name='get_canteens'),
    path('get_stalls/', get_stalls, name='get_stalls'),
    path('get_dishes/', get_dishes, name='get_dishes'),
    path('ranking_seller/', ranking_seller, name='ranking_seller'),
    path('ranking_sumup/', ranking_sumup, name='ranking_sumup'),
    path('ranking_restaurant.html', ranking_restaurant, name='ranking_restaurant'),  # 餐厅排行榜页面
    path('ranking_dishes.html', ranking_dishes, name='ranking_dishes'),  # 菜品排行榜页面
    path('submit_auth/', submit_auth, name='submit_auth'),
    path('submit_feedback/', submit_feedback, name='submit_feedback'),
    path('submit_comment/', submit_comment, name='submit_comment'),
    path('get_comments/', get_comments, name='get_comments'),
    path('get_my_comments/', get_my_comments, name='get_my_comments'),
    path('delete_review/', delete_review, name='delete_review'),
    path('get_stall_comments/', get_stall_comments, name='get_stall_comments'),
    path('get_rating_distribution/', get_rating_distribution, name='get_rating_distribution'),
    path('get_dish_avg_scores/', get_dish_avg_scores, name='get_dish_avg_scores'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
