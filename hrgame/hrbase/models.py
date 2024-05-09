from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum, unique
from django.db.models.signals import post_save
from django.dispatch import receiver

#region enums
@unique
class ProfileRole(models.IntegerChoices):
    NotSelected = 0, 'Не выбран'
    JobSeeker = 1, 'Соискатель'
    Recruiter = 2, 'Рекрутер'

    # def __str__(self):
    #     return self.name
    
    # @classmethod
    # def choices(cls):
    #     return [(i.value, i.name) for i in cls]

    # @property
    def choicesValues(self):
        return [(i.value, i.label) for i in self if i != self.NotSelected]
#endregion  

#region models
class UserExtend(AbstractUser):
    patronymic = models.CharField(max_length=50, blank=True, verbose_name='Отчество')
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name='Аватарка')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    birthday = models.DateField(blank=True, verbose_name='Дата рождения')
    role = models.IntegerField(
        default=ProfileRole.NotSelected.value,
        verbose_name='Тип профиля'
    )

class JobSeekerUser(models.Model):
    user = models.OneToOneField(UserExtend, on_delete=models.CASCADE, related_name='job_seeker')
    about_self = models.TextField(blank=True, verbose_name='О себе')
    score = models.IntegerField(default=0, verbose_name='Рейтинг')
    level = models.IntegerField(default=1, verbose_name='Уровень')
    resume = models.FileField(upload_to='resumes/', blank=True, verbose_name='Резюме')


class RecruiterUser(models.Model):
    user = models.OneToOneField(UserExtend, on_delete=models.CASCADE)
    

#endregion
