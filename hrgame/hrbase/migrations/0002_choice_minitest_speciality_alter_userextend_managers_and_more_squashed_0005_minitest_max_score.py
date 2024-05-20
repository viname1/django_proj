# Generated by Django 5.0.4 on 2024-05-20 06:55

import django.db.models.deletion
import django.utils.timezone
import hrbase.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('hrbase', '0002_choice_minitest_speciality_alter_userextend_managers_and_more'), ('hrbase', '0003_remove_minitestquestionresult_choices_and_more'), ('hrbase', '0004_minitestresult_count_correct_minitestresult_date_and_more'), ('hrbase', '0005_minitest_max_score')]

    dependencies = [
        ('hrbase', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiniTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('pass_score', models.IntegerField(default=0, verbose_name='Порог прохождения')),
                ('max_score', models.IntegerField(default=0, verbose_name='Максимальное количество баллов')),
            ],
        ),
        migrations.CreateModel(
            name='Speciality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
            ],
        ),
        migrations.AlterModelManagers(
            name='userextend',
            managers=[
                ('objects', hrbase.models.UserManagerExtend()),
            ],
        ),
        migrations.AlterField(
            model_name='jobseekeruser',
            name='resume',
            field=models.FileField(blank=True, upload_to=hrbase.models.RandomFileName('resumes/'), verbose_name='Резюме'),
        ),
        migrations.AlterField(
            model_name='userextend',
            name='avatar',
            field=models.ImageField(blank=True, upload_to=hrbase.models.RandomFileName('avatars/'), verbose_name='Аватарка'),
        ),
        migrations.CreateModel(
            name='MiniTestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('is_passed', models.BooleanField()),
                ('minitest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mini_test_result_set', to='hrbase.minitest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mini_test_result_set', to=settings.AUTH_USER_MODEL)),
                ('count_correct', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='Номер вопроса')),
                ('text', models.TextField(verbose_name='Текст вопроса')),
                ('choice_type', models.IntegerField(choices=[(1, 'Один вариант'), (2, 'Несколько вариантов')], default=1, verbose_name='Тип вопроса')),
                ('score', models.IntegerField(default=1, verbose_name='Баллы за вопрос')),
                ('minitest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_set', to='hrbase.minitest', verbose_name='Тест')),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='Номер варианта')),
                ('text', models.TextField(verbose_name='Текст варианта')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Правильный вариант')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choice_set', to='hrbase.question', verbose_name='Вопрос')),
            ],
        ),
        migrations.AddField(
            model_name='jobseekeruser',
            name='speciality',
            field=models.ManyToManyField(blank=True, to='hrbase.speciality', verbose_name='Специальность'),
        ),
        migrations.CreateModel(
            name='MiniTestQuestionResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('minitest_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mini_test_question_result_set', to='hrbase.minitestresult')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hrbase.question')),
                ('is_correct', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='MiniTestChoiceResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hrbase.choice')),
                ('minitest_question_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mini_test_choice_result_set', to='hrbase.minitestquestionresult')),
            ],
        ),
        migrations.AlterField(
            model_name='minitestresult',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mini_test_result_set', to='hrbase.jobseekeruser'),
        ),
        migrations.CreateModel(
            name='SpecialityTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codename', models.CharField(max_length=100, verbose_name='Кодовое имя')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='hrbase.specialitytag', verbose_name='Родитель')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(blank=True, to='hrbase.specialitytag', verbose_name='Теги'),
        ),
        migrations.AlterField(
            model_name='jobseekeruser',
            name='speciality',
            field=models.ManyToManyField(blank=True, to='hrbase.specialitytag', verbose_name='Специальность'),
        ),
    ]