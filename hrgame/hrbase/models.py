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
        """Convert the string value to an int value, or return None."""
        for num, string in cls.choices:
            if string == the_string:
                return num
        return None
#endregion  

#region models
class SpecialityTag(models.Model):
    codename = models.CharField(max_length=100, verbose_name='Кодовое имя')
    name = models.CharField(max_length=100, verbose_name='Название')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Родитель', related_name='children')

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
    score = models.IntegerField(default=0, verbose_name='Рейтинг')
    level = models.IntegerField(default=1, verbose_name='Уровень')
    resume = models.FileField(
        upload_to=RandomFileName('resumes/'),
        blank=True,
        verbose_name='Резюме')
    speciality = models.ManyToManyField(SpecialityTag, blank=True, verbose_name='Специальность')

class RecruiterUser(models.Model):
    user = models.OneToOneField(UserExtend, on_delete=models.CASCADE)

class Speciality(models.Model):
    name = models.TextField(verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

#region test
class MiniTest(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    pass_score = models.IntegerField(default=0, verbose_name='Порог прохождения')
    max_score = models.IntegerField(default=0, verbose_name='Максимальное количество баллов')
    # points = models.IntegerField(default=0, verbose_name='Очки за тест')
    
    def create_from_json_data(data):
        minitest = MiniTest(
            title = data['title'],
            description = data['description'],
            pass_score = data['pass_score'],
        )
        

class Question(models.Model):
    minitest = models.ForeignKey(MiniTest, on_delete=models.CASCADE, verbose_name='Тест', related_name='question_set')
    number = models.IntegerField(verbose_name='Номер вопроса')
    text = models.TextField(verbose_name='Текст вопроса')
    choice_type = models.IntegerField(choices=QuestionType.choices,  default=QuestionType.single, verbose_name='Тип вопроса')
    score = models.IntegerField(default=1, verbose_name='Баллы за вопрос')
    tags = models.ManyToManyField(SpecialityTag, blank=True, verbose_name='Теги')
    
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
    user = models.ForeignKey(JobSeekerUser, on_delete=models.CASCADE, related_name='mini_test_result_set')
    minitest = models.ForeignKey(MiniTest, on_delete=models.CASCADE, related_name='mini_test_result_set')
    score = models.IntegerField()
    is_passed = models.BooleanField()
    date = models.DateTimeField(auto_now_add=True)
    count_correct = models.IntegerField()

class MiniTestQuestionResult(models.Model):
    minitest_result = models.ForeignKey(MiniTestResult, on_delete=models.CASCADE, related_name='mini_test_question_result_set')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # choices = models.ManyToManyField('Choice', blank=True, verbose_name='Выбранные варианты')
    score = models.IntegerField()
    is_correct = models.BooleanField(default=False)

class MiniTestChoiceResult(models.Model):
    minitest_question_result = models.ForeignKey(MiniTestQuestionResult, on_delete=models.CASCADE, related_name='mini_test_choice_result_set')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

#endregion test

#endregion models
