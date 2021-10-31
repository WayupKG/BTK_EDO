import time
import transliterate

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import View, TemplateView, FormView
from django.http import HttpResponseNotFound, HttpResponse
from django.db.models import Q

from .models import Statement, MessageStatement, Document, MovementOfDocument, FileDocument, ReplyDocument, FileReplyDocument
from .forms import CreateDocumentForm, CreateStatementRaportForm
from .tasks import analiz_document, create_notification

from notification.models import Notification
from employee.models import User, Profile

from weasyprint import HTML, CSS


class CreateDocView(LoginRequiredMixin, FormView):
    """Создание Документа"""
    form_class = CreateDocumentForm
    template_name = 'Document/create.html'

    success_url = '/doc/shipped/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Profile.active.all().select_related('position')
        return context

    def form_valid(self, form):
        document = form.save(commit=False)
        document.author = self.request.user.profile
        document.save()
        person = self.request.POST.get('person')
        main_person = 0
        
        for file in self.request.FILES.getlist('files'):
            FileDocument.objects.create(document=document, file=file)
        
        for employee in self.request.POST.getlist('responsible'):
            profile = Profile.objects.get(pk=int(employee))
            if employee == person:
                main_person += 1
                MovementOfDocument.objects.create(document=document, responsible=profile, is_main_person=True)
            else:
                MovementOfDocument.objects.create(document=document, responsible=profile, is_main_person=False)
        if main_person == 0:
            profile = Profile.objects.get(pk=person)
            MovementOfDocument.objects.create(document=document, responsible=profile, is_main_person=True)  
        return super().form_valid(form)


class CreateStatementRaportView(LoginRequiredMixin, FormView):
    """Создание Заявление и Рапорта"""
    form_class = CreateStatementRaportForm
    template_name = 'Document/StatementRaport/create.html'

    success_url = '/doc/stats/shipped/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['directors'] = Profile.active.filter(account__is_director=True)
        return context

    def form_valid(self, form):
        statement = form.save(commit=False)
        statement.author = self.request.user.profile
        statement.type = self.request.POST.get('StatementRaport')
        statement.director = Profile.active.get(pk=self.request.POST.get('director'))
        statement.save()
        return super().form_valid(form)


class InboxDocView(LoginRequiredMixin, TemplateView):
    """Входящие документы"""
    template_name = 'Document/inbox.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['docs'] = MovementOfDocument.objects.filter(responsible=self.request.user.profile).select_related('document__author', 'responsible')
        return context


class InboxStatView(LoginRequiredMixin, TemplateView):
    """Входящие Заявлении и Рапорты для ответственного лица"""
    template_name = 'Document/StatementRaport/inbox.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_statement:
            docs = Statement.objects.filter(responsible=self.request.user.profile).select_related('author', 'director', 'responsible')
        else:
            return HttpResponseNotFound()
        return self.render_to_response(self.get_context_data(docs=docs))


class InboxDirStatView(LoginRequiredMixin, TemplateView):
    """Входящие Заявлении и Рапорты для Директора"""
    template_name = 'Document/StatementRaport/inbox_dir.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_director:
            docs = Statement.objects.filter(director=self.request.user.profile).select_related('author', 'director', 'responsible')
        else:
            return HttpResponseNotFound()
        return self.render_to_response(self.get_context_data(docs=docs))


@login_required()
def remove_inbox_doc(request, slug):
    try:
        doc = get_object_or_404(MovementOfDocument, document__slug=slug, responsible=request.user.profile)
        doc.open_view = True
        doc.datetime_view = timezone.localtime()
        doc.save()
        return redirect('detail-doc-view', slug)
    except:
        return redirect('detail-doc-view', slug)


@login_required()
def remove_inbox_stat(request, slug):
    try:
        doc = get_object_or_404(Statement, slug=slug, responsible=request.user.profile)
        doc.is_open_view_responsible = True
        doc.is_open_view_responsible_date = timezone.localtime()
        doc.save()
        return redirect('detail-stat-view', slug)
    except:
        return redirect('detail-stat-view', slug)


@login_required()
def remove_inbox_stat_director(request, slug):
    try:
        doc = get_object_or_404(Statement, slug=slug, director=request.user.profile)
        doc.is_open_view_director = True
        doc.is_open_view_director_date = timezone.localtime()
        doc.save()
        return redirect('detail-director-view', slug)
    except:
        return redirect('detail-ditector-view', slug)


class InboxDocumentDetailView(LoginRequiredMixin, TemplateView):
    """"""
    template_name = 'Document/Detail/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = FileDocument.objects.filter(document__slug=self.kwargs.get('slug'))
        context['movements'] = MovementOfDocument.objects.filter(document__slug=self.kwargs.get('slug')).select_related('responsible')
        context['movement'] = MovementOfDocument.objects.select_related('document__author', 'responsible').get(
                                                                        document__slug=self.kwargs.get('slug'), 
                                                                        responsible=self.request.user.profile)
        context['answers'] = ReplyDocument.objects.filter(movement=context['movement']).select_related('document', 'movement__responsible')
        context['answers_files'] = FileReplyDocument.objects.filter(movement=context['movement']).select_related('reply')
        return context

    def post(self, *args, **kwargs):
        data = self.request.POST.get
        movement = MovementOfDocument.objects.select_related('document__author', 'responsible').get(document__slug=self.kwargs.get('slug'), 
                                                                                                    responsible=self.request.user.profile)
        if movement.is_send_reply:
            reply = ReplyDocument.objects.create(document=movement.document, movement=movement, 
                                                 appointment=data('appointment'), description=data('body'))
            for file in self.request.FILES.getlist('files'):
                FileReplyDocument.objects.create(movement=movement, reply=reply, file=file)
            body = f'Отправлен ответ на документ с номером {movement.document.number}. Ответ отправил {movement.responsible.get_full_name()}. '\
                    'Чтобы посмотреть ответ нажмите на эту ссылку '\
                   f'<a href="{movement.document.get_absolute_url()}" class="btn btn-light px-5 font-weight-bold" style="font-size: 16px">Подробно</a>'
            create_notification.delay('reply', reply.pk, reply.document.author.pk, reply.document.author.pk, body)
            movement.is_send_reply = False
            movement.save()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class DirectorStatementDetailView(LoginRequiredMixin, TemplateView):
    """"""
    template_name = 'Document/StatementRaport/Detail/base.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_director:
            doc = Statement.objects.select_related('author', 'director', 'responsible').get(
                                                    slug=kwargs.get('slug'), 
                                                    director=self.request.user.profile)
            employees = Profile.objects.filter(account__is_statement=True)
        else:
            return HttpResponseNotFound()
        return self.render_to_response(self.get_context_data(doc=doc, employees=employees, responsible=False))

    def post(self, *args, **kwargs):
        responsible = self.request.POST.get('employee')
        reply = self.request.POST.get('reply')
        message = self.request.POST.get('message')
        statement = Statement.objects.get(slug=kwargs.get('slug'), director=self.request.user.profile)
        if statement.is_editor_director:
            if responsible == 'False' == reply:
                if len(message.replace(' ', '')) > 5:
                    MessageStatement.objects.create(statement=statement, message=message)
                statement.is_editor_director = False
                statement.is_editor_author = True
                statement.status = 'Rejected'
            elif responsible != 'False' and reply == 'True':
                if len(message.replace(' ', '')) > 5:
                    MessageStatement.objects.create(statement=statement, message=message, is_main=True)
                employee = Profile.objects.get(pk=int(responsible))
                statement.is_editor_director = False
                statement.is_editor_responsible = True
                statement.responsible = employee
                statement.status = 'Approved'
            else:
                print('Error')
            statement.save()
        return self.get(*args, **kwargs)


class StatementDetailView(LoginRequiredMixin, TemplateView):
    """"""
    template_name = 'Document/StatementRaport/Detail/base.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_statement:
            doc = Statement.objects.select_related('author', 'director', 'responsible').get(
                                                    slug=self.kwargs.get('slug'), 
                                                    responsible=self.request.user.profile)
        else:
            return HttpResponseNotFound()
        return self.render_to_response(self.get_context_data(doc=doc, responsible=True))


    def post(self, *args, **kwargs):
        statement = Statement.objects.get(slug=self.kwargs.get('slug'), responsible=self.request.user.profile)
        if self.request.POST.get('form_btn') == 'done' and statement.is_editor_responsible:
            statement.status = 'Done'
            statement.save()
        return self.get(*args, **kwargs)


class RenderPDFStatement(LoginRequiredMixin, TemplateView):
    """"""
    def get(self, request, slug, *args, **kwargs):
        statement = Statement.objects.select_related('author', 'director', 'responsible').get(
                                                     Q(slug=slug), Q(author=self.request.user.profile) |
                                                     Q(director=self.request.user.profile) | 
                                                     Q(responsible=self.request.user.profile))
        author = Profile.objects.select_related('account', 'position').get(account=statement.author.account)
        html = render_to_string('Document/StatementRaport/render-pdf.html', {'statement': statement, 'author': author})
        response = HttpResponse(content_type='application/pdf')
        pdf_filename = f'{statement.type}-{transliterate.translit(f"{statement.number}", reversed=True)}.pdf'
        response['Content-Disposition'] = f'filename="{pdf_filename}"'
        HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response, stylesheets=[CSS('static/css/render_statement_pdf.css')], presentational_hints=True)
        return response


class ShippedDocumentView(LoginRequiredMixin, TemplateView):
    """Отправленные документы"""
    template_name = 'Document/Shipped/shipped.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["docs"] = Document.objects.filter(author=self.request.user.profile).select_related('author')
        return context


class ShippedDocumentDetailView(LoginRequiredMixin, TemplateView):
    """"""
    template_name = 'Document/Shipped/Detail/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = FileDocument.objects.filter(document__slug=self.kwargs.get('slug'))
        context['movements'] = MovementOfDocument.objects.filter(document__slug=self.kwargs.get('slug')).select_related('responsible')
        context['document'] = Document.objects.select_related('author').get(slug=self.kwargs.get('slug'), author=self.request.user.profile)
        context['answers'] = ReplyDocument.objects.filter(document=context['document']).select_related('document', 'movement__responsible')
        context['answers_files'] = FileReplyDocument.objects.filter(movement__document=context['document']).select_related('movement', 'reply')
        return context

    def post(self, *args, **kwargs):
        data = self.request.POST.get
        reply = ReplyDocument.objects.select_related('document__author', 
                                                     'movement__responsible').get(pk=int(data('reply')), 
                                                                                  movement__pk=int(data('movement')), 
                                                                                  document__pk=int(data('document')))
        if reply.document.status == 'In_process' and reply.status == 'Waiting':
            if data('accept') == 'to_accept':
                reply.status = 'To_accept'
                reply.movement.status = 'Done'
                body = f'{reply.document.author.position} - {reply.document.author.get_full_name()} '\
                       f'принял ваш ответ отправленный на документ с номером {reply.document.number} <br>'\
                       f'<a href="{reply.document.get_absolute_url_inbox()}" class="btn btn-light px-3 mt-3 font-weight-bold" style="font-size: 15px">Подробно</a>'
            elif data('accept') == 'not_accept':
                reply.status = 'Not_accepted'
                reply.movement.status = 'Not_completed'
                reply.movement.is_send_reply = True
                body = f'{reply.document.author.position} - {reply.document.author.get_full_name()} '\
                       f'отклонил ваш ответ отправленный на документ с номером {reply.document.number}. '\
                       f'Вы можете отправить ответ заново, до истечении срока исполнении. <br>'\
                       f'<a href="{reply.document.get_absolute_url_inbox()}" class="btn btn-light px-3 mt-3 font-weight-bold" style="font-size: 15px">Подробно</a>'
            create_notification.delay('reply', reply.pk, reply.document.author.pk, reply.movement.responsible.pk, body)
            reply.movement.save()
            reply.save()
            if data('accept') == 'to_accept':
                analiz_document.delay(reply.document.pk, reply.document.number)
                time.sleep(3)
        return self.render_to_response(self.get_context_data(**kwargs))


class ShippedStatView(LoginRequiredMixin, TemplateView):
    """Отправленные Заявлении и Рапорты"""
    template_name = 'Document/StatementRaport/shipped.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["docs"] = Statement.objects.filter(author=self.request.user.profile)
        return context


# class ToAcceptReplyDocument(LoginRequiredMixin, View):
#     """"""
#     def get










@login_required()
def doc_view(request, slug):
    doc = get_object_or_404(Document, slug=slug)
    staffs = User.active.all()
    try:
        movement = get_object_or_404(MovementOfDocument, document=doc, responsible=request.user.profile)
    except:
        movement = False
    if request.method == 'POST':
        data = request.POST.get
        redirect_person = data('redirect') if data('redirect') else False
        btn_reply = data('btn_reply') if data('btn_reply') else False
        appointment = data('appointment')
        print(request.POST)
        if movement.document.type != 'Документ' or movement.document.end_date.strftime("%d-%m-%Y") >= timezone.now().strftime("%d-%m-%Y"):
            if btn_reply == 'Выполнено':
                movement.status = 'Выполнено'
                doc.status = 'Выполнено'
            elif btn_reply == 'Не выполнено':
                movement.status = 'Не выполнено'
                doc.status = 'Не выполнено'
            else:
                reply = ReplyDocument.objects.create(document=doc, movement=movement, description=data('body'), appointment=appointment)
                for file in request.FILES.getlist('files'):
                    FileReplyDocument.objects.create(reply=reply, file=file)
                Notification.objects.create(document=doc, user=movement.document.author, reply=reply,
                                            body=create_notification(movement, appointment), type='Ответ')
                if redirect_person:
                    movement.is_main_person = False
                    user_profile = User.objects.get(pk=redirect_person)
                    update_redirect, create_redirect = MovementOfDocument.objects.get_or_create(document=doc, is_main_person=True, is_redirect=True,
                                                                                                defaults={'document': doc, 'responsible': user_profile, 'is_main_person': True, 'is_redirect': True})
                    if not create_redirect:
                        update_redirect.responsible = user_profile
                        update_redirect.save()
            movement.is_open_reply = False
            doc.save(), movement.save()
            error = False
            return redirect('doc_view', slug=doc.slug)
        else:
            error = 'Срок исполнение документа истек'
            return redirect('doc_view', slug=doc.slug)
    else:
        error = False
    return render(request, 'Document/doc_details.html', {'doc': doc, 'movement': movement, 'error': error, 'staffs': staffs})
