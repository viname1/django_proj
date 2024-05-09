from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.contrib.auth import authenticate, login
from hrbase.forms import CommonUserForm, JobSeekerUserForm, RecruiterUserForm, ProfileCreationForm, ProfileUpdateForm, RoleSelectForm
from hrbase.models import JobSeekerUser, RecruiterUser

# Create your views here.

def index(request):
    return render(request, 'index.html')

# def signup(request):
#     return render(request, 'signup.html')

def signup(request):
    if request.method == 'POST':
        form = ProfileCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect('/')
        else:
            return HttpResponse('Введены некорректные данные')

    else:
        form = ProfileCreationForm()
    return render(request, 'signup.html', {'form': form})

def profile(request):
    user = request.user
    if(user.is_authenticated):
        if(request.method == 'POST'):
            if(user.role == 0):
                user.role = request.POST['role']
                user.save()
            else:
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
                    else:
                        return HttpResponse('Введены некорректные данные: ' + str(secondForm.errors))
                else:
                    return HttpResponse('Введены некорректные данные: ' + str(userForm.errors))
                
            return redirect('profile')
        else:
            commonForm = CommonUserForm(instance=user)
            secondForm = None
            if(user.role == 1):
                secondForm = JobSeekerUserForm(instance=user.job_seeker)
            elif(user.role == 2):
                secondForm = RecruiterUserForm(instance=user.recruiter)
            else:
                secondForm = RoleSelectForm()
            return render(request, 'profile.html', {'commonForm': commonForm, 'secondForm': secondForm})
    else:
        return redirect('login')
    
def path(request):
    return render(request, 'path.html')