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
@login_required
def home_dashboard(request):
    context = {
        'total_lockers': Lock.objects.count(),
        'registered_users': User.objects.count(),
        'todays_usage': analytics.get_today_usage(),
        'security_alerts_count': 5,
        # 'lockers': Locker.objects.all(), # Example: Pass actual data
        # 'recent_activities': Activity.objects.order_by('-timestamp')[:4],
        # 'security_alerts': SecurityAlert.objects.filter(is_resolved=False).order_by('-timestamp')[:3],
    }


    recent_activities = (
        Log.objects.select_related("locker", "locker__user")
        .filter(code__in=[1, 2], mark = False)  # 1 info, 2 err[3]
        .order_by("-at_time")
    )

    # Log có code 0 (alert) được coi là Security Alert
    security_alerts_qs = (
        Log.objects.filter(code__in = [0], mark = False)# 0 alter
        .order_by("-at_time")
    )

    context = {
        "total_lockers":      Lock.objects.count(),
        "registered_users":   User.objects.count(),
        "todays_usage":       analytics.get_today_usage(),
        "recent_activities":  recent_activities,
        "security_alerts":    security_alerts_qs,
        "security_alerts_count": security_alerts_qs.count(),
    }

    return render(request, 'accounts/home.html', context)

@login_required
def register_locker_submit(request):
    if request.method == 'POST':
        locker_number = request.POST.get('locker_number')
        locker_location = request.POST.get('locker_location')
        locker_type = request.POST.get('locker_type')

        # Here you would process the data, e.g., save to a Locker model
        # from .models import Locker
        # Locker.objects.create(number=locker_number, location=locker_location, type=locker_type, status='registered')

        messages.success(request, f'Locker {locker_number} registered successfully!')
        return redirect('accounts:home') # Redirect back to dashboard

    return redirect('accounts:home') # Handle non-POST requests or errors

# Add other placeholder views as needed
@login_required
def register_delete_lockers(request):
    return render(request, 'accounts/register_delete_lockers.html')

@login_required
def usage_history(request):
    return render(request, 'accounts/usage_history.html')

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
        print(f"Image file path: {image_file_path}")
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
            print("Request body: ", request.body.decode('utf-8'))
            data = json.loads(request.body.decode('utf-8'))
            passwd = str(data["passwd"])
        except Exception as e:
            print(e)
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
            print(e)
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
        passwd_lock_admin = request.POST.get("passwd_lock_admin")
        code = request.POST.get("code")
        details = request.POST.get("details", "")
        locker_id = request.POST.get("locker_id", None)
        mark = request.POST.get("mark", "false").lower() == "true"

        if not passwd_lock_admin or code is None:
            return JsonResponse({'error': 'Missing required fields'}, status = 400)
        admin = AdminLock.objects.first()
        if not admin or not check_password(passwd_lock_admin, admin.password):
            return JsonResponse({'error': 'Invalid admin password'}, status = 403)
        locker = None
        if(locker_id != None):
            locker = Lock.objects.filter(id = int(locker_id)).first()
            if not locker:
                return JsonResponse({'error': 'Locker not found'}, status = 404)
        try:
            log = Log.objects.create(
                code = int(code),
                details = details,
                locker = locker,
                mark = mark
            )
            return JsonResponse({'success': True, 'log_id': log.id})
        except Exception as e:
            return JsonResponse({'error': f'Failed to write log: {str(e)}'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def api_mark_recent_activity_seen(request):
    try:
        # Only mark logs that are currently "recent activity" (code 1 or 2, mark=True)
        updated = Log.objects.filter(code__in = [1, 2], mark = False).update(mark = True)
        return JsonResponse({'success': True, 'updated': updated})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)