# Generated by Django 5.0.4 on 2024-05-20 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrbase', '0004_minitestresult_count_correct_minitestresult_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='minitest',
            name='max_score',
            field=models.IntegerField(default=0, verbose_name='Максимальное количество баллов'),
        ),
    ]
