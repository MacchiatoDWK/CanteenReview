import os
import random
import time
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from django.core.files.storage import default_storage
from addReview import models
# Create your views here.


def addreview(request):
    userid = request.COOKIES.get('userid')
    usertype = request.COOKIES.get('usertype')
    username = request.COOKIES.get('username')
    if userid is not None and usertype is not None and username is not None:
        return render(request, 'add.html')
    else:
        return render(request, 'add.html', {
            'success': True,
            'msg': '请先登录',
            'back': True
        })


def submit_comment(request):
    rating = request.POST.get('rating')
    if rating is "":
        return render(request, 'add.html', {
            'success': True,
            'msg': '请选择评分',
            'back': False
        })
    else:
        userid = request.COOKIES.get('userid')
        username = request.COOKIES.get('username')
        comment = request.POST.get('comment')
        canteen = request.POST.get('canteen')
        stall = request.POST.get('stall')
        dish = request.POST.get('dish')
        images = request.FILES.getlist('images')
        saved_paths = []
        for image in images:
            # 获取扩展名
            ext = os.path.splitext(image.name)[1]

            # 构造文件名：用户ID_用户名_时间戳_随机数.扩展名
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            rand = random.randint(1000, 9999)
            safe_username = username.replace(' ', '_')
            filename = f"{userid}_{safe_username}_{timestamp}_{rand}{ext}"

            # 保存路径（media/comments/）
            folder = 'comments/'
            save_path = os.path.join(settings.MEDIA_ROOT, folder, filename)
            relative_path = os.path.join(settings.MEDIA_URL, folder, filename)

            # 创建目录
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 保存文件
            with open(save_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            # 收集返回路径
            saved_paths.append(relative_path)

    if stall == "" and dish is None:
        new_comment = models.Review.objects.create(UserID=userid, Username=username, Rating=rating, Describe=comment,
                                     Timestamp=None, ObjType=1, ObjID= canteen)
    else:
        if dish == "":
            new_comment = models.Review.objects.create(UserID=userid, Username=username, Rating=rating,
                                                       Describe=comment,
                                                       Timestamp=None, ObjType=2, ObjID=stall)
        else:
            new_comment = models.Review.objects.create(UserID=userid, Username=username, Rating=rating,
                                                       Describe=comment,
                                                       Timestamp=None, ObjType=3, ObjID=dish)

    for path in saved_paths:
        models.Image.objects.create(ReviewID=new_comment.id, ImageURL=path)

    return render(request, 'add.html', {
        'success': True,
        'msg': '发表成功',
        'back': False
    })
