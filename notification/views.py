from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import View, TemplateView
from django.contrib.auth.hashers import make_password

from .models import Notification
from document.models import ReplyDocument, Document


class NotificationView(LoginRequiredMixin, TemplateView):
    template_name = 'Notification/Notification.html'

    def get(self, *args, **kwargs):
        nots = Notification.objects.filter(user=self.request.user.profile)
        return render(self.request, self.template_name, {'nots': nots})


@login_required()
def remove_notification(request, pk, obj_pk):
    try:
        notification = get_object_or_404(Notification, pk=pk, object_id=obj_pk, user=request.user.profile)
        notification.open_view = True
        notification.save()
        return redirect('single_notification', notification.pk, obj_pk)
    except:
        return redirect('single_notification', notification.pk, obj_pk)


class DetailNotificationView(LoginRequiredMixin, TemplateView):
    template_name = 'Notification/Notification_single.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notification'] = Notification.objects.get(pk=self.kwargs.get('pk'), object_id=self.kwargs.get('obj_pk'), user=self.request.user.profile)
        return context





@login_required()
def single_notification(request, id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, pk=id, user=request.user.profile)
        reply = get_object_or_404(ReplyDocument, pk=notification.reply.pk)
        if request.user == notification.document.author.account:
            if request.POST.get('btn_reply') == 'Принят':
                reply.status = 'Принят'
                reply.save()
                v, person = 0, ''
                for movement in notification.document.movements.all():
                    if movement.status == 'В процессе':
                        v += 1
                    if movement.is_main_person:
                        person = movement.status
                if v == 0 and person == 'Выполнено':
                    notification.document.status = 'Выполнено'
                    notification.document.save()
                return redirect('single_notification', notification.pk, notification.document.slug)
            else:
                reply.status = 'Не принят'
                reply.save()
                return redirect('single_notification', notification.pk, notification.document.slug)
    else:
        notification = get_object_or_404(Notification, pk=id, document__slug=slug, user=request.user.profile)
    return render(request, 'Notification/Notification_single.html', {'notification': notification})
