from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from document.models import Document, MovementOfDocument
from employee.models import User


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'Pages/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['process_count'] = MovementOfDocument.in_process.filter(responsible=self.request.user.profile).count()
        context['done_count'] = MovementOfDocument.done.filter(responsible=self.request.user.profile).count()
        context['not_executed_count'] = MovementOfDocument.not_executed.filter(responsible=self.request.user.profile).count()
        return context


class AddressBookView(LoginRequiredMixin, TemplateView):
    template_name = 'Pages/address_book.html'

    def get(self, request, *args, **kwargs):
        profiles = User.objects.all()
        return render(request, self.template_name, {'profiles': profiles})