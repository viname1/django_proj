
from django.contrib import admin
from hrbase.models import UserExtend, MiniTest, Question, Choice, SpecialityTag




# Register your models here.




admin.site.register(UserExtend)
admin.site.register(MiniTest)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(SpecialityTag)