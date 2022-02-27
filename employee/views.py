from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from home.tasks import send_mail

from .models import Profile, User, SettingsUser
from .forms import UserForm



class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'Pages/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.select_related('account').get(account__pk=kwargs.get('pk'), 
                                                                account__username=kwargs.get('username'))
        return context


class Registration(FormView):
    form_class = UserForm
    success_url = '/accounts/login/'
    template_name = 'registration/register.html'

    def form_valid(self, form):
        data = self.request.POST.get
        profile = form.save(commit=False)
        account = User.objects.create(last_name=profile.last_name, first_name=profile.first_name,
                                      username=data('username'), email=data('email'),
                                      password=make_password(data('password')))
        profile.account = account
        SettingsUser.objects.create(user=account)    
        profile.save()
        body = ['Вы успешно зарегистрированы на сайте edo.btk.kg — Электронный документооборот Бишкекского технического колледжа.',
                'Для входа используйте данные ниже.', f'Email - {profile.email}', f'Пароль - {profile.password}']
        send_mail.delay('Регистрация в электронном документообороте "EDO_BTK"', data('email'), 
                        f'{profile.last_name} {profile.first_name}', body)
        return super(Registration, self).form_valid(form)