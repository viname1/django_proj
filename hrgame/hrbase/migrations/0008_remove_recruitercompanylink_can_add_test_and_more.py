# Generated by Django 5.0.4 on 2024-05-26 16:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrbase', '0007_vacancy_vacancyrequest_delete_speciality_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recruitercompanylink',
            name='can_add_test',
        ),
        migrations.AddField(
            model_name='company',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='owner_company_set', to='hrbase.recruiteruser', verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='recruitercompanylink',
            name='can_edit_test',
            field=models.BooleanField(default=False, verbose_name='Доступность редактирования тестов'),
        ),
        migrations.AddField(
            model_name='recruitercompanylink',
            name='can_edit_vacancy',
            field=models.BooleanField(default=False, verbose_name='Доступность редактирования вакансии'),
        ),
    ]