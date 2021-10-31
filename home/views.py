from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from document.models import Document, MovementOfDocument, Statement
from employee.models import User


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'Pages/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        documents = Document.objects.filter(author=profile).values_list('status')
        movements = MovementOfDocument.objects.filter(responsible=profile).values_list('document__status')
        statements = Statement.objects.filter(author=profile).values_list('status')
        context['m_process_count'] = list(movements).count(('In_process',))
        context['m_done_count'] = list(movements).count(('Done',))
        context['m_not_executed_count'] = list(movements).count(('Not_completed',))

        context['d_process_count'] = list(documents).count(('In_process',))
        context['d_done_count'] = list(documents).count(('Done',))
        context['d_not_executed_count'] = list(documents).count(('Not_completed',))

        context['submitted'] = list(statements).count(('Submitted',))
        context['approved'] = list(statements).count(('Approved',))
        context['rejected'] = list(statements).count(('Rejected',))
        context['done'] = list(statements).count(('Done',))

        context['m_all_count'] = len(movements)
        context['d_all_count'] = len(documents)
        return context


class AddressBookView(LoginRequiredMixin, TemplateView):
    template_name = 'Pages/address_book.html'

    def get(self, request, *args, **kwargs):
        profiles = User.objects.all()
        return render(request, self.template_name, {'profiles': profiles})