from django.http import HttpRequest
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.contrib.auth import authenticate, login
from hrbase.forms import AvatarForm, CommonUserForm, JobSeekerUserForm, RecruiterUserForm, ProfileCreationForm, ProfileUpdateForm, RoleSelectForm
from hrbase.models import JobSeekerUser, RecruiterUser
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

# Create your views here.

def index(request):
    return render(request, 'index.html')

# def signup(request):
#     return render(request, 'signup.html')

def signup(
    request: HttpRequest,
) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = ProfileCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect('/')
        else:
            return HttpResponse(str(form.errors), status=400)
    else:
        form = ProfileCreationForm()
    return render(request, 'signup.html', {'form': form})

def profile(
    request: HttpRequest,
) -> HttpResponse:
    user = request.user
    if(user.is_authenticated == False):
        return redirect('login')
    # Получен ответ из формы
    if(request.method == 'POST'):
        # Сохранить роль пользователя
        user.role = request.POST['role']
        user.save()
    else:
        commonForm = CommonUserForm(instance=user)
        secondForm = None
        avatarForm = AvatarForm(instance=user)
        if(user.role == 1):
            secondForm = JobSeekerUserForm(instance=JobSeekerUser.objects.get_or_create(user=user, defaults={'about_self': 'Default about text'})[0])
        elif(user.role == 2):
            secondForm = RecruiterUserForm(instance=RecruiterUser.objects.get_or_create(user=user)[0])
        else:
            secondForm = RoleSelectForm()
        return render(request, 'profile.html', {'commonForm': commonForm, 'secondForm': secondForm, 'avatarForm': avatarForm})

@login_required
@require_http_methods(['POST'])
def avatar_upload(
    request: HttpRequest,
) -> HttpResponse:
    form = AvatarForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('profile')
    else:
        return HttpResponse(status=400, content='Введены некорректные данные: ' + str(form.errors))

@login_required
def profile_edit(
    request: HttpRequest,
) -> HttpResponse:
    user = request.user
    if(user.is_authenticated == False):
        return redirect('login')
    if(user.role == 0):
        # Пока еще не выбрана роль, нужно сначала выбрать
        return redirect('profile')
    if(request.method == 'POST'):
        userForm = ProfileUpdateForm(request.POST, instance=user)
        secondForm = None
        if(userForm.is_valid()):
            if(user.role == 1):
                job_seeker, created = JobSeekerUser.objects.get_or_create(user=user, defaults={'about_self': 'Default about text'})
                secondForm = JobSeekerUserForm(request.POST, instance=job_seeker)
            elif(user.role == 2):
                recruiter, created = RecruiterUser.objects.get_or_create(user=user)
                secondForm = RecruiterUserForm(request.POST, instance=recruiter)
            if(secondForm.is_valid()):
                userForm.save()
                secondForm.save()
                return redirect('profile')
            else:
                return HttpResponse(status=400, content='Введены некорректные данные: ' + str(secondForm.errors))
        else:
            return HttpResponse(status=400, content='Введены некорректные данные: ' + str(userForm.errors))
    else:
        userForm = CommonUserForm(instance=user)
        secondForm = None
        if(user.role == 1):
            secondForm = JobSeekerUserForm(instance=JobSeekerUser.objects.get_or_create(user=user, defaults={'about_self': 'Default about text'})[0])
        elif(user.role == 2):
            secondForm = RecruiterUserForm(instance=RecruiterUser.objects.get_or_create(user=user)[0])
        else:
            secondForm = RoleSelectForm()
        return render(request, 'profile_edit.html', {'userForm': userForm, 'secondForm': secondForm})

def path(request):
    return render(request, 'path.html')