import datetime
from multiprocessing.managers import BaseManager
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager
from enum import Enum, unique
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import os

from django.utils.deconstruct import deconstructible

@deconstructible
class RandomFileName:
    def __init__(self, sub_dir=''):
        self.sub_dir = sub_dir

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        return os.path.join(self.sub_dir, filename)

#region enums
@unique
class ProfileRole(models.IntegerChoices):
    notSelected = 0, 'Не выбран'
    jobSeeker = 1, 'Соискатель'
    recruiter = 2, 'Рекрутер'

    # def __str__(self):
    #     return self.name
    
    # @classmethod
    # def choices(cls):
    #     return [(i.value, i.name) for i in cls]

    # @property
    def choicesValues(self):
        return [(i.value, i.label) for i in self if i != self.notSelected]

class QuestionType(models.IntegerChoices):
    single = 1, 'Один вариант'
    multiple = 2, 'Несколько вариантов'
    
    def choicesValues(self):
        return [(i.value, i.label) for i in self]
    
    @classmethod
    def string_to_int(cls, the_string):
        for num, string in cls.choices:
            if string == the_string:
                return num
        return None
    
class VacancyRequestStatus(models.IntegerChoices):
    open = 1, 'Открыто'
    interview = 2, 'Собеседование'
    rejected = 3, 'Отказ'
    accepted = 4, 'Принято'
    cancelled_by_user = 5, 'Отменено пользователем'
    
    def choicesValues(self):
        return [(i.value, i.label) for i in self]
    
    @classmethod
    def string_to_int(cls, the_string):
        for num, string in cls.choices:
            if string == the_string:
                return num
        return None
    
#endregion  

#region models
class SpecialityTag(models.Model):
    codename = models.CharField(max_length=100, verbose_name='Кодовое имя', unique=True)
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Родитель', related_name='children')
    
    def __str__(self):
        return self.name

class UserManagerExtend(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        user = UserManager.create_user(self, email=email, password=password, **extra_fields)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('birthday', datetime.date(1900, 1, 1))
        user = UserManager.create_superuser(self, email=email, password=password, **extra_fields)
        return user

class UserExtend(AbstractUser, PermissionsMixin):
    patronymic = models.CharField(max_length=50, blank=True, verbose_name='Отчество')
    avatar = models.ImageField(
        upload_to=RandomFileName('avatars/'),
        blank=True,
        verbose_name='Аватарка')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    birthday = models.DateField(blank=True, verbose_name='Дата рождения')
    role = models.IntegerField(
        default = ProfileRole.notSelected.value,
        verbose_name='Тип профиля')
    objects = UserManagerExtend()

class JobSeekerUser(models.Model):
    user = models.OneToOneField(UserExtend, on_delete=models.CASCADE, related_name='job_seeker')
    about_self = models.TextField(blank=True, verbose_name='О себе')
    # score = models.IntegerField(default=0, verbose_name='Рейтинг')
    level = models.IntegerField(default=1, verbose_name='"Уровень"')
    resume = models.FileField(
        upload_to=RandomFileName('resumes/'),
        blank=True,
        verbose_name='Резюме')
    speciality = models.ManyToManyField(SpecialityTag, blank=True, verbose_name='Специальность')
    
    @property
    def score(self):
        return self.minitest_result_set.filter(is_actual=True, minitest__tags__in=self.speciality.all()).aggregate(models.Sum('score'))

class RecruiterUser(models.Model):
    user = models.OneToOneField(UserExtend, on_delete=models.CASCADE)

class Company(models.Model):
    name = models.TextField(verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активность')

class RecruiterCompanyLink(models.Model):
    user = models.ForeignKey(RecruiterUser, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='company_link_set')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания', related_name='recruiter_link_set')
    can_add_test = models.BooleanField(default=False, verbose_name='Доступность добавления теста')
    is_company_admin = models.BooleanField(default=False, verbose_name='Администратор компании')
    show_in_company_list = models.BooleanField(default=True, verbose_name='Отображать в списке компании')

class Vacancy(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания', related_name='vacancy_set')
    tags = models.ManyToManyField(SpecialityTag, blank=True, verbose_name='Теги')
    is_open = models.BooleanField(default=True, verbose_name='Открыта ли вакансия')
    
class VacancyRequest(models.Model):
    user = models.ForeignKey(JobSeekerUser, on_delete=models.DO_NOTHING, verbose_name='Пользователь', related_name='vacancy_application_set')
    recruiter = models.ForeignKey(RecruiterUser, on_delete=models.DO_NOTHING, verbose_name='Рассматривающий запрос', related_name='vacancy_application_set', blank=True, null=True)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, verbose_name='Вакансия', related_name='vacancy_application_set')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата запроса')
    date_of_interview = models.DateTimeField(blank=True, null=True, verbose_name='Дата собеседования')
    status = models.IntegerField(default=VacancyRequestStatus.open, verbose_name='Статус', choices=VacancyRequestStatus.choices)
    
#region test
class MiniTest(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    pass_score = models.IntegerField(default=0, verbose_name='Порог прохождения')
    max_score = models.IntegerField(default=0, verbose_name='Максимальное количество баллов')
    points = models.IntegerField(default=0, verbose_name='Очки за тест')
    tags = models.ManyToManyField(SpecialityTag, blank=True, verbose_name='Теги')
    author = models.ForeignKey(RecruiterUser, on_delete=models.DO_NOTHING, verbose_name='Автор', related_name='minitest_set', blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name='Компания', related_name='minitest_set', blank=True, null=True)
    custom = models.BooleanField(default=False, verbose_name='Пользовательский тест')
    
    def actual_result(self, user):
        return MiniTestResult.objects.filter(minitest=self, user=user, is_actual=True).first()
    
    def create_from_json_data(data, user=None, company=None):
        minitests = []
        if "minitests" not in data:
            data = {"minitests": [data]}
            
        for data_minitest in data["minitests"]:
            minitest = MiniTest(
                title=data_minitest['title'],
                description=data_minitest['description'],
                pass_score=data_minitest['pass_score'],
                points=data_minitest['points'],
                author=user,
                company=company
            )
            data_questions = data_minitest['questions']
            questions = []
            choices = []
            
            for tag in data_minitest['tags']:
                speciality_tag = SpecialityTag.objects.get(codename=tag)
                minitest.tags.add(speciality_tag)

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
            minitests.append(minitest)

        return minitests
        

class Question(models.Model):
    minitest = models.ForeignKey(MiniTest, on_delete=models.CASCADE, verbose_name='Тест', related_name='question_set')
    number = models.IntegerField(verbose_name='Номер вопроса')
    text = models.TextField(verbose_name='Текст вопроса')
    choice_type = models.IntegerField(choices=QuestionType.choices,  default=QuestionType.single, verbose_name='Тип вопроса')
    score = models.IntegerField(default=1, verbose_name='Баллы за вопрос')
    
    def score_check(self, choices):
        if self.choice_type == QuestionType.single:
            if len(choices) != 1:
                return False, 0
            choice = self.choice_set.filter(number=choices[0]).first()
            return choice.is_correct, choice.is_correct and self.score or 0
        elif self.choice_type == QuestionType.multiple:
            is_correct = True
            for choice in self.choice_set.all():
                if choice.is_correct and choice.number not in choices:
                    is_correct = False
                    break
                if not choice.is_correct and choice.number in choices:
                    is_correct = False
                    break
            if is_correct:
                return True, self.score
            else:
                return False, 0
            
            # correct_choices = [choice for choice in self.choice_set.all() if choice.is_correct and choice.number in choices]
            # if len(correct_choices) == len(choices):
            #     return True, self.score
            # else:
            #     return False, 0
          

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос', related_name='choice_set')
    number = models.IntegerField(verbose_name='Номер варианта')
    text = models.TextField(verbose_name='Текст варианта')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный вариант')

class MiniTestResult(models.Model):
    user = models.ForeignKey(JobSeekerUser, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='mini_test_result_set')
    minitest = models.ForeignKey(MiniTest, on_delete=models.CASCADE, verbose_name='Тест', related_name='mini_test_result_set')
    score = models.IntegerField(default=0, verbose_name='Баллы за тест')
    is_passed = models.BooleanField(default=False, verbose_name='Пройден ли тест')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата прохождения')
    count_correct = models.IntegerField(default=0, verbose_name='Количество правильных ответов')
    is_actual = models.BooleanField(default=True, verbose_name='Актуальность результата')
    
    @property
    def tags(self):
        return self.minitest.tags

class MiniTestQuestionResult(models.Model):
    minitest_result = models.ForeignKey(MiniTestResult, on_delete=models.CASCADE, verbose_name='Тест', related_name='mini_test_question_result_set')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='mini_test_question_result_set')
    score = models.IntegerField(default=0, verbose_name='Баллы за вопрос')
    is_correct = models.BooleanField(default=False, verbose_name='Правильность ответа')

class MiniTestChoiceResult(models.Model):
    minitest_question_result = models.ForeignKey(MiniTestQuestionResult, on_delete=models.CASCADE, verbose_name='Вопрос', related_name='mini_test_choice_result_set')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, verbose_name='Вариант', related_name='mini_test_choice_result_set')

#endregion test

#endregion models
