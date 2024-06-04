from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Company, JobSeekerUser, RecruiterUser, ResumeDocument, SpecialityTag, UserExtend, ProfileRole, Vacancy, RecruiterCompanyLink, VacancyRequest, VacancyRequestStatus


class ProfileCreationForm(UserCreationForm):
    class Meta:
        model = UserExtend
        fields = ['username', 'first_name', 'last_name', 'patronymic', 'phone_number', 'birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'birthday': 'Дата рожденияя'
        }


    def save(self, commit=True):
        user = super(ProfileCreationForm, self).save(commit=False)
        user.patronymic = self.cleaned_data['patronymic']
        user.phone_number = self.cleaned_data['phone_number']
        user.birthday = self.cleaned_data['birthday']

        if commit:
            user.save()
        return user

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # self.helper = FormHelper()
        # self.helper.form_class = 'row g-2'
        # self.helper.field_class = 'mb-4'
        # self.helper.add_input(Submit('submit', 'Submit'))

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserExtend
        fields = ['last_name', 'first_name', 'patronymic', 'avatar', 'phone_number', 'birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'birthday': 'Дата рожденияя'
        }


class CommonUserForm(forms.ModelForm):
    class Meta:
        model = UserExtend
        fields = ['last_name','first_name', 'patronymic', 'phone_number', 'birthday']

class JobSeekerUserForm(forms.ModelForm):
    speciality = forms.ModelMultipleChoiceField(
        queryset=SpecialityTag.objects.all(),
        required=True,
        label='Специальность',
        widget=forms.SelectMultiple(attrs={'data-allow-clear': 'true'})
    )
    class Meta:
        model = JobSeekerUser
        fields = ['about_self', 'speciality']

class RecruiterUserForm(forms.ModelForm):
    class Meta:
        model = RecruiterUser
        fields = []

class RoleSelectForm(forms.Form):
    role = forms.ChoiceField(choices=ProfileRole.choicesValues(ProfileRole))

class AvatarForm(forms.ModelForm):
    class Meta:
        model = UserExtend
        fields = ('avatar',)
        
class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'tags', 'is_open']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(VacancyForm, self).__init__(*args, **kwargs)
        
        if user:
            recruiter_company = RecruiterCompanyLink.objects.filter(user__user=user).first().company
            self.fields['company'].initial = recruiter_company
            self.fields['company'].widget = forms.HiddenInput()

class CompanyForm(forms.ModelForm):

    
    class Meta:
        model = Company
        fields = ['name', 'description', 'owner']
        
    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner', None)
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.fields['owner'].initial = owner
        self.fields['owner'].widget = forms.HiddenInput()

class RecruiterCompanyLinkForm(forms.ModelForm):
    class Meta:
        model = RecruiterCompanyLink
        fields = ['can_edit_test', 'can_edit_vacancy', 'is_company_admin', 'show_in_company_list']
        
class ResumeDocumentForm(forms.ModelForm):
    class Meta:
        model = ResumeDocument
        fields = ['file', 'filename']
        
class VacancyRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = VacancyRequest
        fields = ['date_of_interview', 'status']
        widgets = {
            'date_of_interview': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'status': forms.Select(choices=VacancyRequestStatus.choices)
        }
        labels = {
            'date_of_interview': 'Дата собеседования',
            'status': 'Статус'
        }