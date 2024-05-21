from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import JobSeekerUser, RecruiterUser, SpecialityTag, UserExtend, ProfileRole


class ProfileCreationForm(UserCreationForm):
    class Meta:
        model = UserExtend
        fields = ['username', 'first_name', 'last_name', 'patronymic', 'phone_number', 'birthday']

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
        fields = ['about_self', 'resume', 'speciality']

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