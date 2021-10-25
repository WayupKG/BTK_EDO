from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from home.tasks import send_register_mail

from .models import User, SettingsUser
from .forms import UserForm


@login_required
def profile_view(request, username):
    profile = get_object_or_404(User, account__username=username)
    if request.method == 'POST':
        data = request.POST.get
        if data('form_btn') == 'settings':
            profile.settings.is_mail_inbox = True if data('is_mail_inbox') == 'on' else False
            profile.settings.is_mail_movement = True if data('is_mail_movement') == 'on' else False
            profile.settings.is_mail_ad = True if data('is_mail_ad') == 'on' else False
            profile.settings.save()
            return redirect('Profile', username=request.user.username)
        elif data('form_btn') == 'profile':
            user = get_object_or_404(User, pk=request.user.pk)
            user.email = data('email')
            user.save()
            profile.first_name = data('first_name')
            profile.last_name = data('last_name')
            profile.sur_name = data('sur_name')
            profile.email = data('email')
            profile.tel_number = data('phone')
            profile.date_of_birth = data('date')
            profile.itn = data('itn')
            profile.body = data('body')
            profile.save()
            return redirect('Profile', username=request.user.username)
    return render(request, 'Pages/profile.html', {'profile': profile})



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
        send_register_mail.delay(data('email'), data('password'), profile.last_name, profile.first_name,)
        return super(Registration, self).form_valid(form)