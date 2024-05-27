import json
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
User = settings.AUTH_USER_MODEL
from django.contrib.auth import authenticate, login
from hrbase.forms import AvatarForm, CommonUserForm, CompanyForm, JobSeekerUserForm, RecruiterUserForm, ProfileCreationForm, ProfileUpdateForm, ResumeDocumentForm, RoleSelectForm, VacancyForm
from hrbase.models import JobSeekerUser, RecruiterUser
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Choice, Company, MiniTest, MiniTestChoiceResult, MiniTestQuestionResult, MiniTestResult, Question, QuestionType, RecruiterCompanyLink, ResumeDocument, UserExtend, Vacancy

# Create your views here.

def index(
    request: HttpRequest
) -> HttpResponse:
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
        commonForm = CommonUserForm(instance=user)
        secondForm = None
        avatarForm = AvatarForm(instance=user)
        if(user.role == 1):
            secondForm = JobSeekerUserForm(instance=JobSeekerUser.objects.get_or_create(user=user, defaults={'about_self': 'Default about text'})[0])
        elif(user.role == 2):
            secondForm = RecruiterUserForm(instance=RecruiterUser.objects.get_or_create(user=user)[0])
        else:
            secondForm = RoleSelectForm()
        return render(request, 'profile.html', {'user_seen': user, 'commonForm': commonForm, 'secondForm': secondForm, 'avatarForm': avatarForm, 'ownable': True})

def profile_id(
    request: HttpRequest,
    profile_id: int
) -> HttpResponse:
    user_seen = UserExtend.objects.get(id=profile_id)

    commonForm = CommonUserForm(instance=user_seen)
    secondForm = None
    avatarForm = AvatarForm(instance=user_seen)
    if(user_seen.role == 1):
        secondForm = JobSeekerUserForm(instance=JobSeekerUser.objects.get_or_create(user=user_seen, defaults={'about_self': 'Default about text'})[0])
    elif(user_seen.role == 2):
        secondForm = RecruiterUserForm(instance=RecruiterUser.objects.get_or_create(user=user_seen)[0])
    else:
        secondForm = RoleSelectForm()
    return render(request, 'profile.html', {'user_seen': user_seen, 'commonForm': commonForm, 'secondForm': secondForm, 'avatarForm': avatarForm, 'ownable': request.user.id==user_seen.id})

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

def resume_upload(
    request: HttpRequest
) -> HttpResponse:
    if request.method == 'POST':
        request.POST._mutable = True
        request.POST['user'] = request.user
        form = ResumeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            resume=form.save()
            return JsonResponse({'message': 'File uploaded successfully!'})
        else:
            return JsonResponse({'error': 'Invalid form data.'})
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
    count_correct = 0
    score = 0
    minitest_question_results = []
    minitest_choice_results = []
    
    for question in minitest.question_set.all():
        answers = list(map(int, request.POST.getlist(f'q{question.number}')))
        is_correct, q_score = question.score_check(answers)
        if(is_correct):
            count_correct += 1
        score += q_score
        minitest_question_result = MiniTestQuestionResult(minitest_result=minitest_result, question=question, score=q_score, is_correct=is_correct)
        minitest_question_results.append(minitest_question_result)
        choice_set = question.choice_set.filter(number__in=answers)
        for choice in choice_set:
            minitest_choice_result = MiniTestChoiceResult(
                minitest_question_result=minitest_question_result,
                choice=choice
            )
            minitest_choice_results.append(minitest_choice_result)

    if(score >= minitest.pass_score):
        minitest_result.is_passed = True
    
    MiniTestResult.objects.filter(minitest=minitest, user=minitest_result.user, is_actual=True).exclude(pk=minitest_result.pk).update(is_actual=False)
    
    minitest_result.save()
    for minitest_question_result in minitest_question_results:
        minitest_question_result.save()
    for minitest_choice_result in minitest_choice_results:
        minitest_choice_result.save()
        
    if(minitest_result.is_passed):
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)




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
    return render(request, 'vacancy_list.html', {'company': company, 'vacancy_list': vacancy_list})

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
    request: HttpRequest
) -> HttpResponse:
    vacancy_list = Vacancy.objects.all()
    return render(request, 'vacancy_list.html', {'vacancy_list': vacancy_list})

def vacancy_id(request, vacancy_id):
    vacancy = Vacancy.objects.get(pk=vacancy_id)
    company = Company.objects.get(pk=vacancy.company_id)
    return render(request, 'vacancy.html', {'vacancy': vacancy, 'company': company})

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
        form = VacancyForm(request.POST, user=user, company=Company.objects.get(pk=company_id))
        if form.is_valid():
            form.save()
            return redirect('company_vacancy_list', company_id=company_id)
    else:
        form = VacancyForm(user=user)
    
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