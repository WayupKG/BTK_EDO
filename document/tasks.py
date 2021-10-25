import time

from core.celery import app

from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from employee.models import Profile
from document.models import Document, MovementOfDocument, ReplyDocument, Statement
from check_list.models import CheckList
from notification.models import Notification


@app.task
def create_notification(type: str, pk: int, author_pk: int, profile_pk: int, body: str):
    if type == 'document':
        content = Document.objects.get(pk=pk, author__pk=author_pk)
    elif type == 'movement':
        content = MovementOfDocument.objects.get(pk=pk, document__author__pk=author_pk)
    elif type == 'statement':
        content = Statement.objects.get(pk=pk, author__pk=author_pk)
    elif type == 'reply':
        content = ReplyDocument.objects.get(pk=pk, document__author__pk=author_pk)
    profile = Profile.objects.get(pk=profile_pk)
    Notification.objects.create(content_object=content, body=body, user=profile, type=type)


@app.task
def analiz_document(doc_pk, doc_number):
    document = Document.objects.get(pk=doc_pk, number=doc_number)
    movements = MovementOfDocument.objects.filter(document=document)
    count = 0
    for movement in movements:
        if movement.status == 'Done':
            count += 1
    
    if count == movements.count():
        document.status = 'Done'
        document.save()
        body = f''
        create_notification.delay('document', document.pk, document.author.pk, document.author.pk, body)
    return 


@app.task
def processing_document():
    date_now = timezone.localtime().strftime("%d-%m-%Y")
    documents = Document.objects.filter(status='In_process')
    for document in documents:
        if document.end_date.strftime("%d-%m-%Y") < date_now:
            movements = MovementOfDocument.objects.filter(document=document)
            for movement in movements:
                if movement.status == 'In_process':
                    if movement.answers.all():
                        for reply in movement.answers.all():
                            movement.status = 'Выполнено' if reply.status == 'Выполнено' or reply.status == 'В ожидании' else 'Не выполнено'
                    if not movement.answers.all():
                        movement.status = 'Не выполнено'
                if movement.is_main_person:
                    if movement.appointment == 'Утверждаю' or movement.appointment == 'Согласен' or \
                        movement.appointment == 'Принято к исполнению' or movement.appointment == 'Принято к сведению':
                        document.status = 'Выполнено'
                        movement.status = 'Выполнено'
                    else:
                        if movement.answers.all():
                            for reply in movement.answers.all():
                                movement.status = 'Выполнено' if reply.status == 'Выполнено' or reply.status == 'В ожидании' else 'Не выполнено'
                                document.status = 'Выполнено' if reply.status == 'Выполнено' or reply.status == 'В ожидании' else 'Не выполнено'
                        if not movement.answers.all():
                            movement.status = 'Не выполнено'
                            document.status = 'Не выполнено'
                movement.save()
            document.save()
        time.sleep(3)

