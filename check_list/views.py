import transliterate

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
from .models import CheckList
from weasyprint import HTML, CSS


class CheckListView(LoginRequiredMixin, TemplateView):
    template_name = 'Check_list/check_list.html'
    
    def get(self, request, *args, **kwargs):
        check_lists = CheckList.objects.filter(author=request.user.profile)
        return render(request, self.template_name, {'check_lists': check_lists})


class CheckListPDFView(LoginRequiredMixin, View):

    def get(self, request, key, *args, **kwargs):
        check = CheckList.objects.select_related('document__author', 'author').get(private_key=key)
        html = render_to_string('Check_list/check_list_pdf.html', {'check': check})
        response = HttpResponse(content_type="application/pdf")
        pdf_filename = f'check-{transliterate.translit(f"{check.document.number}", reversed=True)}.pdf'
        response['Content-Disposition'] = f'filename="{pdf_filename}"'
        HTML(string=html, base_url=self.request.build_absolute_uri()).write_pdf(response, stylesheets=[
        CSS('static/css/bootstrap.css'), CSS('static/css/check_list_pdf.css')], presentational_hints=True)
        return response


@login_required()
def remove_check_list(request, key):
    try:
        doc = get_object_or_404(CheckList, private_key=key)
        doc.open_view = True
        doc.datetime_view = timezone.localtime()
        doc.save()
        return redirect('check_list_pdf', key=key)
    except:
        return redirect('check_list_pdf', key=key)