from django.forms import ModelForm, FileInput, TextInput, Select, DateInput, EmailInput
from .models import Profile


class UserForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['last_name', 'first_name', 'sur_name', 'position', 'date_of_birth', 'paul',
                  'tel_number', 'avatar_image']
        widgets = {
            'last_name': TextInput(attrs={'class': 'form-control input-shadow', 'placeholder': 'Фамилия'}),
            'first_name': TextInput(attrs={'class': 'form-control input-shadow', 'placeholder': 'Имя'}),
            'sur_name': TextInput(attrs={'class': 'form-control input-shadow', 'placeholder': 'Отчество'}),
            'position': Select(attrs={'class': 'form-control input-shadow', 'placeholder': 'Должность'}),
            'date_of_birth': DateInput(attrs={'type': 'date', 'class': 'form-control input-shadow',
                                              'placeholder': 'День рождения'}),
            'paul': Select(attrs={'class': 'form-control input-shadow', 'placeholder': 'Пол'}),
            'tel_number': TextInput(attrs={'class': 'form-control input-shadow', 'placeholder': 'Номер телефона'}),
            'avatar_image': FileInput(attrs={'class': 'form-control'})
        }

