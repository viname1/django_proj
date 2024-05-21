# Generated by Django 5.0.4 on 2024-05-20 18:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrbase', '0002_choice_minitest_speciality_alter_userextend_managers_and_more_squashed_0005_minitest_max_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
            ],
        ),
        migrations.RemoveField(
            model_name='question',
            name='tags',
        ),
        migrations.AddField(
            model_name='minitest',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='minitest_set', to='hrbase.recruiteruser', verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='minitest',
            name='points',
            field=models.IntegerField(default=0, verbose_name='Очки за тест'),
        ),
        migrations.AddField(
            model_name='minitest',
            name='tags',
            field=models.ManyToManyField(blank=True, to='hrbase.specialitytag', verbose_name='Теги'),
        ),
        migrations.AlterField(
            model_name='minitestresult',
            name='count_correct',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='minitestresult',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='specialitytag',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='minitest',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='minitest_set', to='hrbase.company', verbose_name='Компания'),
        ),
        migrations.CreateModel(
            name='RecruiterCompanyLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_add_test', models.BooleanField(default=False, verbose_name='Доступность добавления теста')),
                ('is_company_admin', models.BooleanField(default=False, verbose_name='Администратор компании')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hrbase.company', verbose_name='Компания')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hrbase.recruiteruser', verbose_name='Пользователь')),
            ],
        ),
    ]
