from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta, date
from addReview.models import Review, Image
from admin.models import StallInfo, CanteenInfo, DishInfo
from mine.models import UserInfo
from merchant.models import WeeklyReport
import json
from collections import Counter
import re

# Create your views here.

def get_merchant_stalls(request):
    """获取商家名下的档口列表"""
    # 从cookie中获取用户ID
    userid = request.COOKIES.get('userid')
    usertype = request.COOKIES.get('usertype')
    username = request.COOKIES.get('username')
    
    if not userid:
        return JsonResponse({'success': False, 'msg': '请先登录'})
    
    # 获取商家信息
    try:
        user = UserInfo.objects.get(id=userid)
        
        if user.UserType != 2:  # 确保是商家用户
            return JsonResponse({'success': False, 'msg': '无权限访问'})
        
        # 如果商家已经绑定了档口
        if user.StallID:
            try:
                stall = StallInfo.objects.get(id=user.StallID)
                
                canteen = CanteenInfo.objects.get(id=stall.Canteen_id)
                
                response_data = {
                    'success': True,
                    'has_stall': True,
                    'stall': {
                        'id': stall.id,
                        'name': stall.StallName,
                        'canteen_id': canteen.id,
                        'canteen_name': canteen.CanteenName
                    }
                }
                return JsonResponse(response_data)
            except (StallInfo.DoesNotExist, CanteenInfo.DoesNotExist) as e:
                return JsonResponse({
                    'success': False,
                    'has_stall': False,
                    'msg': '档口信息不存在'
                })
        else:
            # 检查是否有待审核的认证申请
            from mine.models import AuthMessage
            auth_msg = AuthMessage.objects.filter(UserID=userid, Validity=1).first()
            
            if auth_msg:
                return JsonResponse({
                    'success': False,
                    'has_stall': False,
                    'pending_auth': True,
                    'msg': '您的档口认证申请正在审核中'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'has_stall': False,
                    'pending_auth': False,
                    'msg': '您尚未绑定档口，请先申请认证'
                })
    except UserInfo.DoesNotExist as e:
        return JsonResponse({'success': False, 'msg': '用户不存在'})

def get_stall_reviews(request):
    """获取档口的所有评论，支持排序"""
    page = int(request.GET.get('page', 1))
    page_size = 10
    sort_by = request.GET.get('sort_by', '-Timestamp')  # 默认按时间降序排序
    
    # 从cookie中获取用户ID
    userid = request.COOKIES.get('userid')
    
    if not userid:
        return JsonResponse({'success': False, 'msg': '请先登录'})
    
    # 获取商家对应的档口ID
    try:
        user = UserInfo.objects.get(id=userid)
        
        if user.UserType != 2:  # 确保是商家用户
            return JsonResponse({'success': False, 'msg': '无权限访问'})
        
        stall_id = user.StallID
        if not stall_id:
            return JsonResponse({'success': False, 'msg': '未关联档口'})
    except UserInfo.DoesNotExist:
        return JsonResponse({'success': False, 'msg': '用户不存在'})
    
    # 使用公共函数获取所有评论
    reviews = get_all_stall_reviews(stall_id)
    
    # 添加排序
    if sort_by == 'rating_high':
        reviews = reviews.order_by('-Rating')
    elif sort_by == 'rating_low':
        reviews = reviews.order_by('Rating')
    else:  # 默认按时间排序
        reviews = reviews.order_by('-Timestamp')
    
    # 分页
    paginator = Paginator(reviews, page_size)
    page_obj = paginator.get_page(page)
    
    # 构造返回数据
    comment_data = []
    for review in page_obj:
        # 获取图片
        images = Image.objects.filter(ReviewID=review.id)
        image_urls = [img.ImageURL for img in images]
        
        # 获取评论对象类型和名称
        obj_type = review.ObjType
        obj_type_name = "未知"
        obj_name = ""
        
        if obj_type == 2:  # 档口评论
            obj_type_name = "档口评论"
            try:
                stall = StallInfo.objects.get(id=review.ObjID)
                obj_name = stall.StallName
            except StallInfo.DoesNotExist:
                obj_name = f"档口#{review.ObjID}"
        elif obj_type == 3:  # 菜品评论
            obj_type_name = "菜品评论"
            try:
                dish = DishInfo.objects.get(id=review.ObjID)
                obj_name = dish.DishName
            except DishInfo.DoesNotExist:
                obj_name = f"菜品#{review.ObjID}"
        
        # 构造评论数据
        comment_data.append({
            'username': review.Username,
            'rating': review.Rating,
            'text': review.Describe,
            'timestamp': review.Timestamp.strftime("%Y-%m-%d %H:%M"),
            'images': image_urls,
            'reviewId': review.id,
            'objType': obj_type,
            'objTypeName': obj_type_name,
            'objName': obj_name,
        })
    
    # 返回评论数据和分页信息
    return JsonResponse({
        'success': True,
        'comments': comment_data,
        'has_next': page_obj.has_next(),
        'total_pages': paginator.num_pages,
        'current_page': page
    })

def get_all_stall_reviews(stall_id):
    """获取档口的所有评论（包括菜品评论），不分页，不排序"""
    
    # 查询与档口相关的评论
    # ObjType=2 表示评论对象是档口，ObjID=stall_id 表示评论的是当前档口
    stall_reviews = Review.objects.filter(ObjType=2, ObjID=stall_id)
    
    # 查询该档口下所有菜品的评论
    # ObjType=3 表示评论对象是菜品
    from admin.models import DishInfo
    dish_ids = list(DishInfo.objects.filter(Stall_id=stall_id).values_list('id', flat=True))
    
    dish_reviews = Review.objects.filter(ObjType=3, ObjID__in=dish_ids)
    
    # 合并档口评论和菜品评论
    from django.db.models import Q
    reviews = Review.objects.filter(
        Q(ObjType=2, ObjID=stall_id) |  # 档口评论
        Q(ObjType=3, ObjID__in=dish_ids)  # 菜品评论
    )
    
    return reviews

def generate_weekly_report(request):
    """生成档口周报，不限制时间周期"""
    try:
        # 从cookie中获取用户ID
        userid = request.COOKIES.get('userid')
        
        if not userid:
            return JsonResponse({'success': False, 'msg': '请先登录'})
        
        # 获取商家对应的档口ID
        try:
            user = UserInfo.objects.get(id=userid)
            
            if user.UserType != 2:  # 确保是商家用户
                return JsonResponse({'success': False, 'msg': '无权限访问'})
            
            stall_id = user.StallID
            if not stall_id:
                return JsonResponse({'success': False, 'msg': '未关联档口'})
        except UserInfo.DoesNotExist:
            return JsonResponse({'success': False, 'msg': '用户不存在'})
        
        # 获取时间范围参数，默认为最近7天
        try:
            days = int(request.GET.get('days', 7))
        except ValueError:
            days = 7  # 如果转换失败，使用默认值
        
        end_date = timezone.now().date()
        
        # 如果选择"全部"，设置一个很早的开始日期，而不是None
        if days > 0:
            start_date = end_date - timedelta(days=days)
        else:
            # 使用一个很早的日期作为开始日期，比如2020年1月1日
            start_date = datetime(2020, 1, 1).date()
        
        # 使用公共函数获取所有评论
        reviews = get_all_stall_reviews(stall_id)
        
        # 如果选择了特定时间范围（非"全部"选项）
        if days > 0:
            # 应用时间筛选
            try:
                filtered_reviews = reviews.filter(
                    Timestamp__date__gte=start_date,
                    Timestamp__date__lte=end_date
                )
                reviews = filtered_reviews
            except Exception as e:
                # 手动筛选
                filtered_reviews = []
                for review in reviews:
                    if start_date <= review.Timestamp.date() <= end_date:
                        filtered_reviews.append(review)
                reviews = filtered_reviews
        
        # 计算最终的评论总数，处理可能的列表类型
        if isinstance(reviews, list):
            total_reviews = len(reviews)
        else:
            total_reviews = reviews.count()
        
        # 计算平均评分
        avg_rating = 0
        if total_reviews > 0:
            if isinstance(reviews, list):
                # 手动计算平均评分
                ratings_sum = sum(review.Rating for review in reviews)
                avg_rating = ratings_sum / total_reviews
            else:
                avg_rating = reviews.aggregate(Avg('Rating'))['Rating__avg'] or 0
        
        # 计算评分分布
        if isinstance(reviews, list):
            # 手动计算评分分布
            rating_counts = {
                '5分': sum(1 for review in reviews if review.Rating == 5),
                '4分': sum(1 for review in reviews if review.Rating == 4),
                '3分': sum(1 for review in reviews if review.Rating == 3),
                '2分': sum(1 for review in reviews if review.Rating == 2),
                '1分': sum(1 for review in reviews if review.Rating == 1),
            }
            # 手动计算好评、中评、差评数量
            high_rating = sum(1 for review in reviews if review.Rating >= 4)
            mid_rating = sum(1 for review in reviews if 2 <= review.Rating < 4)
            low_rating = sum(1 for review in reviews if review.Rating < 2)
        else:
            # 使用查询集计算
            rating_counts = {
                '5分': reviews.filter(Rating=5).count(),
                '4分': reviews.filter(Rating=4).count(),
                '3分': reviews.filter(Rating=3).count(),
                '2分': reviews.filter(Rating=2).count(),
                '1分': reviews.filter(Rating=1).count(),
            }
            # 计算好评、中评、差评数量
            high_rating = reviews.filter(Rating__gte=4).count()
            mid_rating = reviews.filter(Rating__gte=2, Rating__lt=4).count()
            low_rating = reviews.filter(Rating__lt=2).count()
        
        # 计算评分分布百分比
        rating_percentages = {}
        if total_reviews > 0:
            for key, value in rating_counts.items():
                rating_percentages[key] = round((value / total_reviews) * 100, 1)
        else:
            # 如果没有评论，所有评分占比为0
            for key in rating_counts.keys():
                rating_percentages[key] = 0
        
        # 提取常见关键词
        if total_reviews > 0:
            try:
                all_text = ' '.join([review.Describe for review in reviews if review.Describe])
                # 简单的关键词提取，实际项目中可以使用更复杂的NLP方法
                words = re.findall(r'[\u4e00-\u9fa5]{2,}', all_text)  # 提取中文词语
                word_count = Counter(words).most_common(10)
                common_keywords = json.dumps(dict(word_count), ensure_ascii=False)
            except Exception as e:
                common_keywords = json.dumps({}, ensure_ascii=False)
        else:
            common_keywords = json.dumps({}, ensure_ascii=False)
        
        # 保存周报到数据库
        report = WeeklyReport.objects.create(
            StallID=stall_id,
            StartDate=start_date,
            EndDate=end_date,
            TotalReviews=total_reviews,
            AverageRating=avg_rating or 0,
            HighRatingCount=high_rating,
            MidRatingCount=mid_rating,
            LowRatingCount=low_rating,
            CommonKeywords=common_keywords
        )
        
        # 获取档口信息
        try:
            stall = StallInfo.objects.get(id=stall_id)
            stall_name = stall.StallName
            canteen = CanteenInfo.objects.get(id=stall.Canteen_id)
            canteen_name = canteen.CanteenName
        except (StallInfo.DoesNotExist, CanteenInfo.DoesNotExist):
            stall_name = "未知档口"
            canteen_name = "未知食堂"
        
        # 返回周报数据
        return JsonResponse({
            'success': True,
            'report': {
                'id': report.id,
                'stall_id': stall_id,
                'stall_name': stall_name,
                'canteen_name': canteen_name,
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d"),
                'total_reviews': total_reviews,
                'average_rating': round(avg_rating, 1) if avg_rating else 0,
                'high_rating_count': high_rating,
                'mid_rating_count': mid_rating,
                'low_rating_count': low_rating,
                'rating_counts': rating_counts,
                'rating_percentages': rating_percentages,
                'common_keywords': json.loads(common_keywords) if common_keywords else {},
                'created_at': report.CreatedAt.strftime("%Y-%m-%d %H:%M")
            }
        })
    except Exception as e:
        # 捕获所有异常，确保返回有用的错误信息
        return JsonResponse({
            'success': False, 
            'msg': f'生成周报失败: {str(e)}',
            'error_type': str(type(e).__name__)
        })

def get_report_history(request):
    """获取档口的历史周报"""
    # 从cookie中获取用户ID
    userid = request.COOKIES.get('userid')
    if not userid:
        return JsonResponse({'success': False, 'msg': '请先登录'})
    
    # 获取商家对应的档口ID
    try:
        user = UserInfo.objects.get(id=userid)
        if user.UserType != 2:  # 确保是商家用户
            return JsonResponse({'success': False, 'msg': '无权限访问'})
        
        stall_id = user.StallID
        if not stall_id:
            return JsonResponse({'success': False, 'msg': '未关联档口'})
    except UserInfo.DoesNotExist:
        return JsonResponse({'success': False, 'msg': '用户不存在'})
    
    # 获取档口的所有周报，按创建时间降序排序
    reports = WeeklyReport.objects.filter(StallID=stall_id).order_by('-CreatedAt')
    
    # 构造返回数据
    report_list = []
    for report in reports:
        report_list.append({
            'id': report.id,
            'start_date': report.StartDate.strftime("%Y-%m-%d"),
            'end_date': report.EndDate.strftime("%Y-%m-%d"),
            'total_reviews': report.TotalReviews,
            'average_rating': round(report.AverageRating, 1),
            'created_at': report.CreatedAt.strftime("%Y-%m-%d %H:%M")
        })
    
    return JsonResponse({
        'success': True,
        'reports': report_list
    })

def get_report_detail(request):
    """获取指定ID的周报详情"""
    # 从cookie中获取用户ID
    userid = request.COOKIES.get('userid')
    if not userid:
        return JsonResponse({'success': False, 'msg': '请先登录'})
    
    # 获取商家对应的档口ID
    try:
        user = UserInfo.objects.get(id=userid)
        if user.UserType != 2:  # 确保是商家用户
            return JsonResponse({'success': False, 'msg': '无权限访问'})
        
        stall_id = user.StallID
        if not stall_id:
            return JsonResponse({'success': False, 'msg': '未关联档口'})
    except UserInfo.DoesNotExist:
        return JsonResponse({'success': False, 'msg': '用户不存在'})
    
    # 获取周报ID
    try:
        report_id = int(request.GET.get('report_id', 0))
        if report_id <= 0:
            return JsonResponse({'success': False, 'msg': '参数错误'})
    except ValueError:
        return JsonResponse({'success': False, 'msg': '参数错误'})
    
    # 获取周报详情
    try:
        report = WeeklyReport.objects.get(id=report_id, StallID=stall_id)
    except WeeklyReport.DoesNotExist:
        return JsonResponse({'success': False, 'msg': '周报不存在或无权访问'})
    
    # 获取档口信息
    try:
        stall = StallInfo.objects.get(id=stall_id)
        stall_name = stall.StallName
        canteen = CanteenInfo.objects.get(id=stall.Canteen_id)
        canteen_name = canteen.CanteenName
    except (StallInfo.DoesNotExist, CanteenInfo.DoesNotExist):
        stall_name = "未知档口"
        canteen_name = "未知食堂"
    
    # 解析评分分布和关键词
    try:
        common_keywords = json.loads(report.CommonKeywords)
    except:
        common_keywords = {}
    
    # 计算评分分布百分比
    rating_counts = {
        '5分': 0,
        '4分': 0,
        '3分': 0,
        '2分': 0,
        '1分': 0
    }
    
    # 根据好评、中评、差评数量估算各评分的分布
    if report.HighRatingCount > 0:
        # 假设好评中4分和5分的比例为4:6
        rating_counts['4分'] = int(report.HighRatingCount * 0.4)
        rating_counts['5分'] = report.HighRatingCount - rating_counts['4分']
    
    if report.MidRatingCount > 0:
        # 假设中评中2分和3分的比例为3:7
        rating_counts['2分'] = int(report.MidRatingCount * 0.3)
        rating_counts['3分'] = report.MidRatingCount - rating_counts['2分']
    
    if report.LowRatingCount > 0:
        # 假设差评全部为1分
        rating_counts['1分'] = report.LowRatingCount
    
    # 计算评分百分比
    rating_percentages = {}
    if report.TotalReviews > 0:
        for key, value in rating_counts.items():
            rating_percentages[key] = round((value / report.TotalReviews) * 100, 1)
    else:
        for key in rating_counts.keys():
            rating_percentages[key] = 0
    
    # 返回周报数据
    return JsonResponse({
        'success': True,
        'report': {
            'id': report.id,
            'stall_id': stall_id,
            'stall_name': stall_name,
            'canteen_name': canteen_name,
            'start_date': report.StartDate.strftime("%Y-%m-%d"),
            'end_date': report.EndDate.strftime("%Y-%m-%d"),
            'total_reviews': report.TotalReviews,
            'average_rating': round(report.AverageRating, 1),
            'high_rating_count': report.HighRatingCount,
            'mid_rating_count': report.MidRatingCount,
            'low_rating_count': report.LowRatingCount,
            'rating_counts': rating_counts,
            'rating_percentages': rating_percentages,
            'common_keywords': common_keywords,
            'created_at': report.CreatedAt.strftime("%Y-%m-%d %H:%M")
        }
    })
