# web/views.py

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from lockers.models import Lock, User, Log, UserImage, AdminLock
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, Http404
import os
from . import analytics
from rest_framework import generics, permissions
import json
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password

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
        .filter(code__in=[1, 2])
        .order_by("-at_time")
    )

    # Log có code 0 (alert) hoặc 2 (error) được coi là Security Alert
    security_alerts_qs = (
        Log.objects.filter(code__in=[0])            # 0 alter, 2 err[3]
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
    
    return render(request, 'accounts/user_information.html')

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
        if User.objects.filter(sdt=sdt).exists():
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
def api_upload_user_image(request):
    if request.method == 'POST':
        try:
            if 'image' not in request.FILES:
                return JsonResponse({'error': 'No image file provided'}, status = 400)
            image_file = request.FILES.get("image")
            print(request.body.decode('utf-8'))
            data = json.loads(json.loads(request.data.decode('utf-8')))
            user = User.objects.filter(id = int(data["user_id"])).first()
            password = make_password(str(data["password"]))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status = 400)
        
        if not user:
            return JsonResponse({'error': 'User not found'}, status = 404)
        

        # Save image to Image model
        img = Image.objects.create(title=f"image_user_{user_id}", image = image_file)
        # Link to user (replace old avatar if exists)
        UserImage.objects.update_or_create(user = user, defaults={'image': img})
        return JsonResponse({'message': 'Image User uploaded successfully', 'image_url': img.image.url})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status = 405)

@csrf_exempt
def api_get_user_image(request, user_id, passwd):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return JsonResponse({'error': 'User not found'}, status=404)
    try:
        avatar = user.avatar
        if avatar.image and avatar.image.image:
            return JsonResponse({'image_url': avatar.image.image.url})
        else:
            return JsonResponse({'error': 'No avatar image set'}, status = 404)
    except UserAvatar.DoesNotExist:
        return JsonResponse({'error': 'No avatar image set'}, status = 404)