from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import CheckList
from weasyprint import HTML, CSS


class CheckListView(LoginRequiredMixin, TemplateView):
    template_name = 'Check_list/check_list.html'
    
    def get(self, request, *args, **kwargs):
        check_lists = CheckList.objects.filter(author=request.user.profile)
        return render(request, self.template_name, {'check_lists': check_lists})


class CheckListPDFView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        check = get_object_or_404(CheckList, private_key=kwargs.get('slug'))
        html = render_to_string('Check_list/check_list_pdf.html', {'check': check})
        response = HttpResponse(content_type="application/pdf")
        response["Content-Dispositions"] = f"filename='check_{check.id}.pdf'"
        HTML(string=html, base_url=self.request.build_absolute_uri()).write_pdf(response, stylesheets=[
        CSS('static/css/bootstrap.css'), CSS('static/css/check_list_pdf.css')], presentational_hints=True)
        return response
