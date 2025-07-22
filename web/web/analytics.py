from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from lockers.models import Log, Lock, User

def get_locker_statistics():
    """Lấy thống kê tủ khóa"""
    return {
        'total_lockers': Lock.objects.count(),
        'registered_lockers': Lock.objects.filter(user__isnull = False).count(),
        'unregistered_lockers': Lock.objects.filter(user__isnull = True).count(),
        'registered_users': User.objects.count(),
    }

def get_today_usage():
    """Đếm số lần sử dụng hôm nay"""
    today = datetime.now().date()
    return Log.objects.filter(at_time__date = today).count()

def get_unprocessed_error_logs():
    return Log.objects.filter(
        code = 2,
        mark = False
    ).order_by('-at_time')

def get_unprocessed_alerts_logs():
    return Log.objects.filter(
        code = 0,
        mark = False
    ).order_by('-at_time')