"""
URL configuration for web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView # Import RedirectView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home_dashboard, name='home'),
    path("login/", auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/',auth_views.LogoutView.as_view(), name="logout"),

    path('lockers/', views.lockers, name='lockers'),
    path('usage-history/', views.usage_history, name='usage_history'),
    path('user-information/', views.user_information, name='user_information'),
    path('get_user_image/<int:user_id>/', views.get_user_image, name='get_user_image'),
    path('security-alerts/', views.security_alerts, name='security_alerts'),
    path('change_password/', views.change_password, name='change_password'),
    path('all_log/', views.all_log, name='all_log'),
    path('', RedirectView.as_view(pattern_name='home', permanent=False)),

    path('api/register_user/', views.api_user_register, name='api_user_register'),
    path('api/change_passwd_lock_admin', views.api_change_passwd_lock_admin, name='change_passwd_lock_admin'),
    path('api/get_user_image/', views.api_get_user_image, name='api_get_user_image'),
    path('api/check_passwd_lock_admin', views.api_check_passwd_lock_admin, name='check_passwd_lock_admin'),
    path('api/toggle_user_status/', views.api_toggle_user_status, name='api_toggle_user_status'),
    path('api/edit_user/', views.api_edit_user, name='api_edit_user'),
    #path('api/update_user_vector/', views.api_update_user_vector, name='api_update_user_vector'),
    #path('api/get_user_vector/', views.api_get_user_vector, name='api_get_user_vector'),
    path('api/write_log/', views.api_write_log, name='api_write_log'),
    path('api/mark_recent_activity_seen/', views.api_mark_recent_activity_seen, name='api_mark_recent_activity_seen'),
    path('api/mark_security_alerts_seen/', views.api_mark_security_alerts_seen, name='api_mark_security_alerts_seen'),
    path('api/delete_user/', views.api_delete_user, name='api_delete_user'),
    path('api/get_user_list/', views.api_get_user_list, name='api_get_user_list'),
    path('api/usage_history/', views.api_usage_history, name='api_usage_history'),
    path('api/get_lockers_by_board/', views.api_get_lockers_by_board, name='api_get_lockers_by_board'),
    path('api/all_log/', views.api_all_log, name='api_all_log'),
    path('api/recent_activities/', views.api_recent_activities, name='api_recent_activities'),
    path('api/security_alerts/', views.api_security_alerts, name='api_security_alerts'),
    path('api/dashboard_stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/users/<int:user_id>/lockers/', views.api_user_lockers_json, name='api_user_lockers_json'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)