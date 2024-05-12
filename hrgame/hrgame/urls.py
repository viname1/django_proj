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
    path('profile/edit', views.profile_edit, name='profile_edit'),
    path('path', views.path, name='path'),
    path('signup/', views.signup, name='signup'),
    # path('signup/jobseeker', views.signup_jobseeker),
    # path('signup/recruiter', views.signup),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', next_page='/profile/'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html', next_page='/login/'), name='logout'),
    path('avatar_upload/', views.avatar_upload, name='avatar_upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

