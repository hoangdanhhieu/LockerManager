# web/views.py

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from lockers.models import Lock, User, Log, UserImage, AdminLock, Image
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, Http404
import os
from . import analytics
from rest_framework import generics, permissions
import json
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from . import settings
from . import function
from django.core.paginator import Paginator
from django.db.models import Q
@login_required
def home_dashboard(request):
    
    # Create locks for boards 1-32, each with lock_ids 1-16
    #locks_to_create = []
    #for board_id in range(1, 33):  # 1 to 32
    #    for lock_id in range(1, 17):  # 1 to 16
    #        locks_to_create.append(Lock(board_id=board_id, lock_id=lock_id))


    recent_activities = (
        Log.objects.select_related("locker", "locker__user")
        .filter(code__in=[0, 1, 2, 3, 5, 6], mark = False)
        .order_by("-at_time")
    )

    security_alerts_qs = (
        Log.objects.filter(code__in = [4], mark = False)
        .select_related("locker")
        .order_by("-at_time")
    )

    security_alerts_with_lockinfo = []
    
    for alert in security_alerts_qs:
        security_alerts_with_lockinfo.append({
            "id": alert.id,
            "details": alert.details,
            "at_time": alert.at_time,
            "board_id": alert.locker.board_id if alert.locker else None,
            "lock_id": alert.locker.lock_id if alert.locker else None,
        })
        
    context = {
        "total_lockers":      Lock.objects.filter(user__isnull = False).count(),
        "registered_users":   User.objects.count(),
        "todays_usage":       analytics.get_today_usage(),
        "recent_activities":  recent_activities,
        "security_alerts":    security_alerts_with_lockinfo,
        "security_alerts_count": len(security_alerts_with_lockinfo),
    }

    return render(request, 'accounts/home.html', context)

# Add other placeholder views as needed
@login_required
def lockers(request):
    return render(request, 'accounts/lockers.html')

@login_required
def usage_history(request):
    context = {
        "range32": range(1, 33),
        "range16": range(1, 17)
    }
    return render(request, 'accounts/usage_history.html', context)

@login_required
def all_log(request):
    context = {
        "range32": range(1, 33),
        "range16": range(1, 17)
    }
    return render(request, 'accounts/all_log.html', context)


@login_required
def user_information(request):
    users = User.objects.all()
    user_data = []
    for user in users:
        # Get user image (if exists)
        user_image = UserImage.objects.filter(user = user).first()
        image_url = reverse('get_user_image', args = [user.id])
        # Get last access time from Log (assuming code=1 or 2 means access)
        last_log = Log.objects.filter(locker__user = user, code__in=[1,2]).order_by('-at_time').first()
        last_access = last_log.at_time if last_log else user.RegTime
        user_data.append({
            'id': user.id,
            'name': user.name,
            'sdt': user.sdt,
            'status': user.status,
            'image_url': image_url,
            'reg_time': user.RegTime,
            'last_access': last_access,
        })
    return render(request, 'accounts/user_information.html', {'users': user_data})

@login_required
def get_user_image(request, user_id):
    user = User.objects.filter(id = user_id).first()
    if not user:
        return JsonResponse({'error': 'User not found'}, status=404)
    user_image = UserImage.objects.filter(user=user).first()
    if user_image and user_image.image and user_image.image.image:
        image_file = user_image.image.image
        response = FileResponse(image_file.open('rb'), content_type='image/jpeg')
        response['Content-Disposition'] = f'inline; filename="{image_file.name.split("/")[-1]}"'
        return response
    else:
        image_file_path = os.path.join(settings.MEDIA_ROOT, 'images', 'user_null.png')
        response = FileResponse(open(image_file_path, 'rb'), content_type='image/png')
        response['Content-Disposition'] = 'inline; filename="user_null.png"'
        return response


@login_required
def security_alerts(request):
    return render(request, 'accounts/security_alerts.html')

@login_required
def change_password(request):
    return render(request, 'accounts/change_password.html')

@login_required
def api_user_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(json.loads(request.body.decode('utf-8')))
            name = str(data["name"])
            sdt = str(data["sdt"])
            status = int(data["status"])
            if((len(name) + len(sdt)) == 0):
                raise
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Check if sdt already exists
        if User.objects.filter(sdt = sdt).exists():
            return JsonResponse({'error': 'Phone number already exists'}, status = 400)
        # Lưu vào database
        try:
            new_user = User(name = name, sdt = sdt, status = status)
            new_user.save()
            new_user_id = new_user.id
            function.write_log(10, user_id = new_user_id)
        except Exception as e:
            return JsonResponse({'error': f'Database save failed: {str(e)}'}, status = 500)
        return JsonResponse({'message': 'Data saved successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status = 405)

@login_required
def api_edit_user(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_id = data.get('id')
        name = data.get('name')
        sdt = data.get('sdt')
        status = int(data.get('status'))

        # Check if sdt exists for another user
        if User.objects.filter(sdt = sdt).exclude(id = user_id).exists():
            return JsonResponse({'success': False, 'error': 'Phone number already exists for another user.'}, status=400)

        user = User.objects.get(id=user_id)
        user.name = name
        user.sdt = sdt
        user.status = status
        user.save()
        function.write_log(7, user_id = user_id)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status = 400)

@login_required
def api_change_passwd_lock_admin(request):
    if request.method == 'POST':
        try:
            data = json.loads(json.loads(request.body.decode('utf-8')))
            current_password = str(data["current_password"])
            new_password = str(data["new_password"])
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status = 400)

        # Check if admin exists
        if(AdminLock.objects.count() == 0):
            new_admin = AdminLock(password = make_password(new_password))
            new_admin.save()
        else:
            admin = AdminLock.objects.first()
            if(not check_password(current_password, admin.password)):
                return JsonResponse({'error': 'Current password is incorrect'}, status = 400)
            admin.password = make_password(new_password)
            admin.save()
        return JsonResponse({'message': 'Change password successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status = 405)

@csrf_exempt
def api_check_passwd_lock_admin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            passwd = str(data["passwd"])
        except Exception as e:
            return JsonResponse({'error': 'Invalid JSON'}, status = 400)

        admin = AdminLock.objects.first()
        if not admin:
            return JsonResponse({'error': 'Admin password not set'}, status=404)
        if check_password(passwd, admin.password):
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid password'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)    

@csrf_exempt
def api_upload_user_image(request):
    if request.method == 'POST':
        try:
            passwd_lock_admin = request.POST.get("passwd_lock_admin")
            user_id = request.POST.get("user_id")
            image_file = request.FILES.get("image")
            if not passwd_lock_admin or not user_id or not image_file:
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            admin = AdminLock.objects.first()
            if not admin or not check_password(passwd_lock_admin, admin.password):
                return JsonResponse({'error': 'Invalid admin password'}, status=403)
            user = User.objects.filter(id=int(user_id)).first()
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)
            img = Image.objects.create(title=f"image_user_{user_id}", image=image_file)
            UserImage.objects.update_or_create(user=user, defaults={'image': img})
            return JsonResponse({'message': 'Image User uploaded successfully', 'image_url': img.image.url})
        except Exception as e:
            return JsonResponse({'error': 'Invalid data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def api_get_user_image(request):
    if request.method == 'POST':
        try:
            passwd_lock_admin = request.POST.get("passwd_lock_admin")
            user_id = request.POST.get("user_id")
            if not passwd_lock_admin or not user_id:
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            admin = AdminLock.objects.first()
            if not admin or not check_password(passwd_lock_admin, admin.password):
                return JsonResponse({'error': 'Invalid admin password'}, status=403)
            user = User.objects.filter(id=int(user_id)).first()
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)
            user_image = UserImage.objects.filter(user=user).first()
            if user_image and user_image.image and user_image.image.image:
                image_file = user_image.image.image
                response = FileResponse(image_file.open('rb'), content_type='image/jpeg')
                response['Content-Disposition'] = f'attachment; filename="{image_file.name.split("/")[-1]}"'
                return response
            else:
                return JsonResponse({'error': 'No avatar image set'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Invalid data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def api_update_user_vector(request):
    if request.method == 'POST':
        passwd_lock_admin = request.POST.get("passwd_lock_admin")
        user_id = request.POST.get("user_id")
        vector = request.POST.get("vector")
        if not passwd_lock_admin or not user_id or vector is None:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        admin = AdminLock.objects.first()
        if not admin or not check_password(passwd_lock_admin, admin.password):
            return JsonResponse({'error': 'Invalid admin password'}, status=403)
        user = User.objects.filter(id=int(user_id)).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        try:
            user.vector_id = json.loads(vector)
            user.save()
            function.write_log(8, user_id = user_id)
            return JsonResponse({'success': True, 'message': 'Vector updated successfully'})
        except Exception as e:
            return JsonResponse({'error': f'Invalid vector format: {str(e)}'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def api_get_user_vector(request):
    if request.method == 'POST':
        passwd_lock_admin = request.POST.get("passwd_lock_admin")
        user_id = request.POST.get("user_id")
        if not passwd_lock_admin or not user_id:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        admin = AdminLock.objects.first()
        if not admin or not check_password(passwd_lock_admin, admin.password):
            return JsonResponse({'error': 'Invalid admin password'}, status=403)
        user = User.objects.filter(id=int(user_id)).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        return JsonResponse({'success': True, 'vector_id': user.vector_id})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def api_write_log(request):
    if request.method == 'POST':
        try:
            passwd_lock_admin = request.POST.get("passwd_lock_admin")
            code = request.POST.get("code")
            details = request.POST.get("details", "")
            locker_id = request.POST.get("locker_id", None)
            board_id = request.POST.get("board_id", None)
            if not passwd_lock_admin or code is None or not code.isdigit():
                return JsonResponse({'error': 'Missing required fields'}, status = 400)
            admin = AdminLock.objects.first()
            if not admin or not check_password(passwd_lock_admin, admin.password):
                return JsonResponse({'error': 'Invalid admin password'}, status = 403)
            locker = None
            if(locker_id != None and board_id != None):
                locker = Lock.objects.filter(lock_id = int(locker_id), board_id=int(board_id)).first()
                if not locker:
                    return JsonResponse({'error': 'Locker not found'}, status = 404)
                locker_id = int(locker_id)
                board_id = int(board_id)
            code = int(code)
            return function.write_log(code, details, locker)
        except Exception as e:
            return JsonResponse({'error': f'Failed to write log: {str(e)}'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def api_mark_recent_activity_seen(request):
    try:
        updated = Log.objects.filter(code__in = [0, 1, 2, 3, 5, 6], mark = False).update(mark = True)
        return JsonResponse({'success': True, 'updated': updated})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def api_mark_security_alerts_seen(request):
    try:
        updated = Log.objects.filter(code__in = [4], mark = False).update(mark = True)
        return JsonResponse({'success': True, 'updated': updated})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def api_delete_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_id = data.get('user_id')
            user = User.objects.filter(id = user_id).first()
            if not user:
                return JsonResponse({'success': False, 'error': 'User not found'}, status = 404)
            user.delete()
            function.write_log(9, user_id = user_id)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status = 400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status = 405)

@csrf_exempt
def api_get_user_list(request):
    if request.method == 'POST':
        try:
            passwd_lock_admin = request.POST.get("passwd_lock_admin")
            if not passwd_lock_admin:
                return JsonResponse({'error': 'Missing admin password'}, status=400)
            admin = AdminLock.objects.first()
            if not admin or not check_password(passwd_lock_admin, admin.password):
                return JsonResponse({'error': 'Invalid admin password'}, status=403)
            users = User.objects.all().values('id', 'name', 'status')
            user_list = [
                {'userid': u['id'], 'name': u['name'], 'status': u['status']}
                for u in users
            ]
            return JsonResponse({'success': True, 'users': user_list})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def api_get_lockers_by_board(request):
    if request.method == 'GET':
        try:
            board = request.GET.get('board')
            if not board:
                return JsonResponse({'success': False, 'error': 'Missing board parameter'}, status=400)
            if board == 'all':
                lockers = Lock.objects.select_related('user').all()
            else:
                lockers = Lock.objects.select_related('user').filter(board_id=board)
            data = [
                {
                    'locker_id': locker.lock_id,
                    'board_id': locker.board_id,
                    'user': locker.user.name if locker.user else None,
                    'user_id': locker.user.id if locker.user else None,
                    'status': 'registered' if locker.user else 'unregistered'
                }
                for locker in lockers
            ]
            return JsonResponse({'success': True, 'lockers': data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def api_usage_history(request):
    if request.method == 'GET':
        # Lấy tham số filter từ URL
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        user_id = request.GET.get('user_id')
        board_id = request.GET.get('board_id')
        locker_id = request.GET.get('locker_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        logs = Log.objects.select_related("locker", "locker__user").filter(code__in=[1, 3, 4])
        # Áp dụng bộ lọc nếu có
        if user_id != ''and user_id:
            logs = logs.filter(Q(locker__user__name__icontains = user_id) | Q(locker__user__sdt = user_id))
        if board_id != '' and board_id != 'all' and board_id:
            logs = logs.filter(locker__board_id = board_id)
        if locker_id != '' and locker_id != 'all' and locker_id:
            logs = logs.filter(locker__lock_id = locker_id)
        if start_date != '' and start_date:
            logs = logs.filter(at_time__gte = start_date)
        if end_date != '' and end_date:
            logs = logs.filter(at_time__lte = end_date)

        logs = logs.order_by('-at_time')
        paginator = Paginator(logs, per_page)
        page_obj = paginator.get_page(page)

        data = []
        for log in page_obj:
            data.append({
                'date_time': log.at_time.strftime('%Y-%m-%d %H:%M'),
                'user': f'User #{log.locker.user.id} {log.locker.user.name}' if log.locker and log.locker.user else '',
                'board': f'#{log.locker.board_id:02d}' if log.locker else '',
                'locker': f'#{log.locker.lock_id:03d}' if log.locker else '',
                'action': 'Access' if log.code == 1 else 'Failed Access'
            })
        return JsonResponse({
            'success': True,
            'logs': data,
            'total': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number
        })
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def api_all_log(request):
    if request.method == 'GET':
        # Lấy tham số filter từ URL
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        user_id = request.GET.get('user_id')
        board_id = request.GET.get('board_id')
        locker_id = request.GET.get('locker_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        logs = Log.objects.select_related("locker", "locker__user")
        # Áp dụng bộ lọc nếu có
        if user_id != ''and user_id:
            logs = logs.filter(Q(locker__user__name__icontains = user_id) | Q(locker__user__sdt = user_id))
        if board_id != '' and board_id != 'all' and board_id:
            logs = logs.filter(locker__board_id = board_id)
        if locker_id != '' and locker_id != 'all' and locker_id:
            logs = logs.filter(locker__lock_id = locker_id)
        if start_date != '' and start_date:
            logs = logs.filter(at_time__gte = start_date)
        if end_date != '' and end_date:
            logs = logs.filter(at_time__lte = end_date)

        logs = logs.order_by('-at_time')
        paginator = Paginator(logs, per_page)
        page_obj = paginator.get_page(page)

        data = []
        for log in page_obj:
            data.append({
                'id': log.id,
                'details': log.details,
                'date_time': log.at_time.strftime('%Y-%m-%d %H:%M'),
                'user': f'User #{log.locker.user.id} {log.locker.user.name}' if log.locker and log.locker.user else '',
                'board': f'#{log.locker.board_id:02d}' if log.locker else '',
                'locker': f'#{log.locker.lock_id:03d}' if log.locker else '',
            })
        return JsonResponse({
            'success': True,
            'logs': data,
            'total': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number
        })
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def api_toggle_user_status(request):
    if( request.method != 'POST'):
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_id = data.get('user_id')
        user = User.objects.get(id = user_id)
        user.status = 0 if user.status else 1  # Toggle status
        user.save()
        return JsonResponse({'success': True, 'new_status': user.status})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)