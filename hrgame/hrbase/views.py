from datetime import timezone
import json
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
User = settings.AUTH_USER_MODEL
from django.contrib.auth import authenticate, login
from hrbase.forms import AvatarForm, CommonUserForm, CompanyForm, JobSeekerUserForm, RecruiterUserForm, ProfileCreationForm, ProfileUpdateForm, ResumeDocumentForm, RoleSelectForm, VacancyForm, VacancyRequestUpdateForm
from hrbase.models import JobSeekerUser, RecruiterUser
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Choice, Company, LevelStatus, MiniTest, MiniTestChoiceResult, MiniTestQuestionResult, MiniTestResult, Question, QuestionType, RecruiterCompanyLink, ResumeDocument, UserExtend, Vacancy, VacancyRequest, VacancyRequestStatus

# Create your views here.

def index(
    request: HttpRequest
) -> HttpResponse:
    return redirect('profile')
    # return render(request, 'index.html')

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

@login_required
def profile(
    request: HttpRequest,
) -> HttpResponse:
    user = request.user
    # Получен ответ из формы
    if(request.method == 'POST'):
        # Сохранить роль пользователя
        user.role = request.POST['role']
        user.save()
        return redirect('profile')
    else:
        return profile_id(request, request.user.id)
        
def profile_id(
    request: HttpRequest,
    profile_id: int
) -> HttpResponse:
    user_seen = UserExtend.objects.get(id=profile_id)

    commonForm = CommonUserForm(instance=user_seen)
    secondForm = None
    avatarForm = AvatarForm(instance=user_seen)
    minitest_results = None
    if(user_seen.role == 1):
        secondForm = JobSeekerUserForm(instance=JobSeekerUser.objects.get_or_create(user=user_seen, defaults={'about_self': 'Default about text'})[0])
        minitest_results = MiniTestResult.objects.filter(user=user_seen.job_seeker, is_actual=True)
    elif(user_seen.role == 2):
        secondForm = RecruiterUserForm(instance=RecruiterUser.objects.get_or_create(user=user_seen)[0])
    else:
        secondForm = RoleSelectForm()
    return render(request, 'profile.html', {'user_seen': user_seen, 'commonForm': commonForm, 'secondForm': secondForm, 'avatarForm': avatarForm, 'ownable': request.user.id==user_seen.id, 'minitest_results': minitest_results})

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

def resume_list(
    request: HttpRequest,
    user_id: int = None
) -> HttpResponse:
    if user_id is None:
        user_id = request.user.id
    resume_list = ResumeDocument.objects.filter(user=user_id)
    owner = JobSeekerUser.objects.get(id=user_id)
    return render(request, 'resume_list.html', {'resume_list': resume_list, 'owner': owner, 'ownable': request.user.id==user_id})

@login_required
def resume_upload(
    request: HttpRequest
) -> HttpResponse:
    if request.method == 'POST':
        request.POST._mutable = True
        # request.POST['user'] = request.user.job_seeker.id
        form = ResumeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            form.instance.user = user.job_seeker
            resume=form.save()
            if user.job_seeker.level < LevelStatus.minitests:
                user.job_seeker.level = LevelStatus.minitests
                user.job_seeker.save()
            return JsonResponse({'message': 'File uploaded successfully!'})
        else:
            return JsonResponse({'error': 'Invalid form data.'})
    return redirect('resume_list')

@login_required
@require_http_methods(['POST'])
def reset_level(request):
    request.user.job_seeker.level = LevelStatus.vacancy
    request.user.job_seeker.save()

@login_required
def resume_toggle_visibility(request, resume_id):
    resume = ResumeDocument.objects.get(id=resume_id)
    resume.visible = not resume.visible
    resume.save()
    return JsonResponse({'visible': resume.visible})

@login_required
def resume_delete(request, resume_id):
    resume = ResumeDocument.objects.get(id=resume_id)
    resume.delete()
    return redirect('resume_list')

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

@login_required
def path(
    request: HttpRequest
) -> HttpResponse:
    return render(request, 'path.html')

@login_required
def minitest(
    request: HttpRequest,
    minitest_id: int
) -> HttpResponse:
    minitest = MiniTest.objects.get(pk=minitest_id)
    return render(request, 'minitest.html', {'minitest': minitest})

@login_required
def minitest_list(
    request: HttpRequest
) -> HttpResponse:
    user = request.user
    minitest_list = None
    if(user.role == 1):
        job_seeker_user = JobSeekerUser.objects.get(user=user)
        minitest_list = MiniTest.objects.filter(tags__in=job_seeker_user.speciality.all(), custom=False).distinct()
    return render(request, 'minitest_list.html', {'minitest_list': minitest_list})

@require_http_methods(['POST'])
@login_required
def minitest_submit(
    request: HttpRequest,
    minitest_id: int
) -> HttpResponse:
    minitest = MiniTest.objects.get(pk=minitest_id)
    minitest_result = MiniTestResult(user=request.user.job_seeker, minitest=minitest, score=0, is_passed=False, is_actual=True)
    minitest_result = minitest.create_result(request.user.job_seeker, request.POST)        
    if(minitest_result.is_passed):
        if request.user.role == 1 and request.user.job_seeker.level < LevelStatus.vacancy:
            request.user.job_seeker.level = LevelStatus.vacancy
            request.user.job_seeker.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

def minitest_result(
    request: HttpRequest,
    minitest_result_id: int
) -> HttpResponse:
    minitest_result = MiniTestResult.objects.get(pk=minitest_result_id) 
    return render(request, 'minitest_result.html', {'minitest_result': minitest_result})

@require_http_methods(['POST'])
@login_required
def upload_minitest(
    request: HttpRequest
) -> HttpResponse:
    company_id=request.POST['company']
    minitest=None
    if company_id:
        company = Company.objects.get(pk=company_id)
        request.user.recruiteruser.add_test_company(company, json.load(request.FILES['json_file']))
    else:
        if request.user.is_staff == False:
            return HttpResponse(status=403)
        MiniTest.create_from_json_data(json.load(request.FILES['json_file']))
    
    if company_id:
        return redirect('company_minitest_list', company_id=company_id)
    else:
        return redirect('minitest_list')

    
def company_list(
    request: HttpRequest
) -> HttpResponse:
    if(request.user.role == 2):
        links = request.user.recruiteruser.company_link_set
        managed_company_list = Company.objects.filter(pk__in=links.values('company_id'))
        company_list = Company.objects.exclude(pk__in=links.values('company_id'))
        return render(request, 'company_list.html', {'managed_company_list': managed_company_list, 'company_list': company_list})
    else:
        return render(request, 'company_list.html', {'company_list': Company.objects.all()})

def company_id(
    request: HttpRequest,
    company_id: int
) -> HttpResponse:
    company = Company.objects.get(pk=company_id)
    return render(request, 'company.html', {'company': company})

def company_vacancy_list(
    request: HttpRequest,
    company_id: int
) -> HttpResponse:
    company = Company.objects.get(pk=company_id)
    vacancy_list = Vacancy.objects.filter(company=company, is_open=True).all()
    can_edit_vacancy = False
    if company_id:
        company = Company.objects.get(pk=company_id)
        vacancy_list = Vacancy.objects.filter(company=company).all()
        if(request.user.role == 2):
            link = RecruiterCompanyLink.objects.filter(user=request.user.recruiteruser, company=company).first()
            can_edit_vacancy = link and (link.is_company_admin or link.can_edit_vacancy)
    return render(request, 'vacancy_list.html', {'company': company, 'vacancy_list': vacancy_list, 'can_edit_vacancy': can_edit_vacancy})

def company_minitest_list(
    request: HttpRequest,
    company_id: int
) -> HttpResponse:
    company = Company.objects.get(pk=company_id)
    minitest_list = MiniTest.objects.filter(company=company).all()
    can_edit_test = False
    if(request.user.is_staff):
        can_edit_test = True
    if(request.user.role == 2):
        link = RecruiterCompanyLink.objects.filter(user=request.user.recruiteruser, company=company).first()
        can_edit_test = link and (link.is_company_admin or link.can_edit_test)
    return render(request, 'minitest_list.html', {'company': company, 'minitest_list': minitest_list, 'can_edit_test': can_edit_test})

def company_create(
    request: HttpRequest
) -> HttpResponse:
    if request.method == 'POST':
        form = CompanyForm(request.POST, owner=request.user)
        if form.is_valid():
            company = form.save()
            RecruiterCompanyLink.objects.create(
                user=request.user.recruiteruser,
                company=company,
                is_company_admin=True,
            )
            return redirect('company_list')
    else:
        form = CompanyForm()
    return render(request, 'company_create.html', {'form': form})

def vacancy_list(
    request: HttpRequest, open_only: bool = False
) -> HttpResponse:
    vacancy_list = None
    if open_only:
        vacancy_list = Vacancy.objects.filter(is_open=True).all()
    else:
        vacancy_list = Vacancy.objects.all()
    return render(request, 'vacancy_list.html', {'vacancy_list': vacancy_list})

def vacancy_id(request, vacancy_id):
    vacancy = Vacancy.objects.get(pk=vacancy_id)
    company = Company.objects.get(pk=vacancy.company_id)
    active_vacancy_request = None
    if request.user.role == 1:
        job_seeker_user = JobSeekerUser.objects.get(user=request.user)
        active_vacancy_request = vacancy.vacancy_request_set.filter(status=VacancyRequestStatus.open or VacancyRequestStatus.accepted).first()
    return render(request, 'vacancy.html', {'vacancy': vacancy, 'company': company, 'active_vacancy_request': active_vacancy_request})

@login_required
def vacancy_create(
    request: HttpRequest,
    company_id: int
) -> HttpResponse:
    user = request.user.recruiteruser
    company = Company.objects.get(pk=company_id)
    link = RecruiterCompanyLink.objects.filter(user=user, company=company).first()
    if not link or not(link.is_company_admin or link.can_add_vacancy):
        return HttpResponse(status=403, content="У вас нет прав создавать вакансии на данную компанию")
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            form.instance.company=Company.objects.get(pk=company_id)
            form.save()
            return redirect('company_vacancy_list', company_id=company_id)
    else:
        form = VacancyForm()
    
    return render(request, 'vacancy_create.html', {'form': form})

@login_required
def create_company(
    request: HttpRequest
) -> HttpResponse:
    user = request.user
    if user.role != 2:
        return HttpResponse(status=403)
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            RecruiterCompanyLink.objects.create(
                user=user.recruiteruser,
                company=company,
                is_company_admin=True,
                can_add_test=True
            )
            return redirect('company_detail', company_id=company.id)
    else:
        form = CompanyForm()
    return render(request, 'create_company.html', {'form': form})

def vacancy_request_create(request, vacancy_id):
    if request.user.role != 1:
        return HttpResponse(status=403)
    if request.user.job_seeker.level != LevelStatus.vacancy:
        return HttpResponse(status=403)
    vacancy = Vacancy.objects.get(pk=vacancy_id)
    VacancyRequest.objects.create(
        user=request.user.job_seeker,
        vacancy=vacancy,
        status=VacancyRequestStatus.open
    )
    request.user.job_seeker.level = LevelStatus.interview
    request.user.job_seeker.save()
    return redirect('vacancy_list')

def vacancy_request_list(request):
    vacancy_request_list = None
    if request.user.role == 1:
        job_seeker_user = JobSeekerUser.objects.get(user=request.user)
        vacancy_request_list = job_seeker_user.vacancy_request_set.all()
    if request.user.role == 2:
        links = RecruiterCompanyLink.objects.filter(user=request.user.recruiteruser)
        if links:
            companies = [link.company for link in links]
            vacancy_request_list = VacancyRequest.objects.filter(vacancy__company__in=companies)
    
    return render(request, 'vacancy_request_list.html', {'vacancy_request_list': vacancy_request_list})

@login_required
def vacancy_request_cancel(request, request_id):
    vacancy_request = VacancyRequest.objects.get(pk=request_id)
    if request.user.role != 1 or request.user.job_seeker != vacancy_request.user:
        return HttpResponse(status=403) 
    vacancy_request.status = VacancyRequestStatus.cancelled_by_user
    vacancy_request.save()
    if vacancy_request.date_of_interview < timezone.now():
        # Пользователь не прошел собеседование
        request.user.job_seeker.level = LevelStatus.minitests
    else:
        request.user.job_seeker.level = LevelStatus.vacancy
    request.user.job_seeker.save()
    return redirect('vacancy_request_list')

def vacancy_request_edit(request, request_id):
    vacancy_request = VacancyRequest.objects.get(pk=request_id)
    if request.method == 'POST':
        form = VacancyRequestUpdateForm(request.POST, instance=vacancy_request)
        if form.is_valid():
            form.instance.recruiter = request.user.recruiteruser
            form.save()
            return redirect('vacancy_requests_list')    
    else:
        form = VacancyRequestUpdateForm(instance=vacancy_request)

    return render(request, 'vacancy_request_edit.html', {'form': form, 'vacancy_request': vacancy_request})

def vacancy_request_detail(request, request_id):
    vacancy_request = VacancyRequest.objects.get(pk=request_id)
    if request.method == 'POST':
        form = VacancyRequestUpdateForm(request.POST, instance=vacancy_request)
        if form.is_valid():
            form.save()
            return redirect('vacancy_request_detail', request_id=request_id)
    else:
        form = VacancyRequestUpdateForm(instance=vacancy_request)

    return render(request, 'vacancy_request_detail.html', {
        'vacancy_request': vacancy_request,
        'form': form
    })