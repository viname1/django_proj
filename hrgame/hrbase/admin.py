
from django.contrib import admin
from hrbase.models import Company, JobSeekerUser, MiniTestResult, RecruiterUser, UserExtend, MiniTest, Question, Choice, SpecialityTag, Vacancy




# Register your models here.




admin.site.register(UserExtend)
admin.site.register(JobSeekerUser)
admin.site.register(RecruiterUser)
admin.site.register(MiniTest)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(SpecialityTag)
admin.site.register(MiniTestResult)
admin.site.register(Company)
admin.site.register(Vacancy)