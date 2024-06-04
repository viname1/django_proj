"""
URL configuration for hrgame project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from hrbase import views


urlpatterns = [
    path('', views.index),
    path('admin/', admin.site.urls),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:profile_id>/', views.profile_id, name='profile_id'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    path('path', views.path, name='path'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html', next_page='/profile/'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='logout.html', next_page='/accounts/login/'), name='logout'),
    path('avatar_upload/', views.avatar_upload, name='avatar_upload'),
    path('minitest', views.minitest_list, name='minitest_list'),
    path('minitest/<int:minitest_id>/', views.minitest, name='minitest_start'),
    path('minitest_submit/<int:minitest_id>/', views.minitest_submit, name='minitest_submit'),
    path('minitest_result/<int:minitest_result_id>/', views.minitest_result, name='minitest_result'),
    path('minitest/upload', views.upload_minitest, name='upload_minitest'),
    path('company', views.company_list, name='company_list'),
    path('company/<int:company_id>/', views.company_id, name='company_id'),
    path('company/<int:company_id>/vacancy', views.company_vacancy_list, name='company_vacancy_list'),
    path('company/<int:company_id>/minitest', views.company_minitest_list, name='company_minitest_list'),
    path('company/<int:company_id>/vacancy/create', views.vacancy_create, name='vacancy_create'),
    path('company/create', views.company_create, name='company_create'),
    path('vacancy', views.vacancy_list, name='vacancy_list'),
    path('vacancy_open', views.vacancy_list, {'open_only': True}, name='vacancy_list_open'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_id, name='vacancy_id'),
    path('vacancy/<int:vacancy_id>/apply/', views.vacancy_request_create, name='vacancy_request_create'),
    path('vacancy_requests/', views.vacancy_request_list, name='vacancy_request_list'),
    path('vacancy_requests/<int:request_id>/cancel/', views.vacancy_request_cancel, name='vacancy_request_cancel'),
    path('vacancy_requests/<int:request_id>/update/', views.vacancy_request_edit, name='vacancy_request_edit'),
    path('profile/<int:user_id>/resumes', views.resume_list, name='resume_list'),
    path('resumes', views.resume_list, name='resume_list'),
    path('resumes/<int:resume_id>/toggle_visibility/', views.resume_toggle_visibility, name='resume_toggle_visibility'),
    path('resumes/<int:resume_id>/delete/', views.resume_delete, name='resume_delete'),
    path('resume_upload/', views.resume_upload, name='resume_upload'),
    path('reset_level/', views.reset_level, name='reset_level'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

