import json
from django.http import HttpRequest
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.contrib.auth import authenticate, login
from hrbase.forms import AvatarForm, CommonUserForm, JobSeekerUserForm, RecruiterUserForm, ProfileCreationForm, ProfileUpdateForm, RoleSelectForm
from hrbase.models import JobSeekerUser, RecruiterUser
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Choice, MiniTest, MiniTestChoiceResult, MiniTestQuestionResult, MiniTestResult, Question, QuestionType


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
        return render(request, 'profile.html', {'commonForm': commonForm, 'secondForm': secondForm, 'avatarForm': avatarForm})

def profile_id(request, profile_id):
    user_seen = UserExtend.objects.get(id=profile_id)

    commonForm = CommonUserForm(instance=user_seen)
    secondForm = None
    avatarForm = AvatarForm(instance=user_seen)
    if(user.role == 1):
        secondForm = JobSeekerUserForm(instance=JobSeekerUser.objects.get_or_create(user=user_seen, defaults={'about_self': 'Default about text'})[0])
    elif(user.role == 2):
        secondForm = RecruiterUserForm(instance=RecruiterUser.objects.get_or_create(user=user_seen)[0])
    else:
        secondForm = RoleSelectForm()
    return render(request, 'profile.html', {'commonForm': commonForm, 'secondForm': secondForm, 'avatarForm': avatarForm, 'ownable': request.user.id==user.id})



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

@login_required
def path(request):
    return render(request, 'path.html')

@login_required
def minitest(request, minitest_id):
    minitest = MiniTest.objects.get(pk=minitest_id)
    return render(request, 'minitest.html', {'minitest': minitest})

@login_required
def minitest_list(request):
    user = request.user
    minitest_list = None
    if(user.role == 1):
        job_seeker_user = JobSeekerUser.objects.get(user=user)
        minitest_list = MiniTest.objects.filter(tags__in=job_seeker_user.speciality.all(), custom=False).distinct()
    return render(request, 'minitest_list.html', {'minitest_list': minitest_list})

@require_http_methods(['POST'])
@login_required
def minitest_submit(request, minitest_id):
    minitest = MiniTest.objects.get(pk=minitest_id)
    minitest_result = MiniTestResult(user=request.user, minitest=minitest, score=0, is_passed=False)
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
def upload_minitest(request):
    if(request.user.is_staff == False):
        return HttpResponse(status=403)
    data = json.load(request.FILES['json_file'])
    minitest = MiniTest(
        title=data['title'],
        description=data['description'],
        pass_score=data['pass_score'],
    )
    data_questions = data['questions']
    questions = []
    choices = []
    for i, data_question in enumerate(data_questions):
        question = Question(
            minitest=minitest,
            text=data_question['text'],
            number=i + 1,
            choice_type=getattr(QuestionType, data_question['type']),
            score=data_question['score'],
        )
        questions.append(question)
        
        for j, data_choice in enumerate(data_question['options']):
            choice = Choice(
                question=question,
                text=data_choice['text'],
                number=j + 1,
                is_correct=data_choice.get('is_correct', False),
            )
            choices.append(choice)
            
    minitest.save()
    for question in questions:
        question.save()
    for choice in choices:
        choice.save()
    
            
    
    return HttpResponse(status=200)

    
    
