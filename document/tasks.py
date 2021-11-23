from core.celery import app

from django.utils import timezone

from employee.models import Profile
from document.models import Document, MovementOfDocument, ReplyDocument, Statement
from notification.models import Notification
from check_list.models import CheckList
from home.tasks import send_mail


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
def create_check_list(doc_pk: int, author_pk: int, status: str):
    doc = Document.objects.get(pk=doc_pk)
    profile = Profile.objects.get(pk=author_pk)
    update, create = CheckList.objects.get_or_create(document=doc, author=profile, 
                                                     defaults={'document': doc, 'author': profile, 'status': status})
    if not create:
        update.status = status
        update.save()


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
        create_check_list.delay(document.pk, document.author.pk, document.status)
        body = f'Документ с номером {document.number}, было выполнено. Чтобы узнать подробно о документе нажмите на эту ссылку <br>'\
               f'<a href="{document.get_absolute_url()}" class="btn btn-light px-3 mt-3 font-weight-bold" style="font-size: 15px">Подробно</a>'
        create_notification.delay('document', document.pk, document.author.pk, document.author.pk, body)
    return 


@app.task
def processing_document():
    date_now = timezone.localtime()
    documents = Document.objects.filter(status='In_process').select_related('author')
    messages = [f'Дата - {timezone.localtime().strftime("%d-%m-%Y")}']
    count_ = 0
    for document in documents:
        in_process, not_completed, done, is_main_person = 0, 0, 0, 'Errors'
        new_day,  new_month, new_year = int(timezone.localtime().strftime("%d")), int(timezone.localtime().strftime("%m")), int(timezone.localtime().strftime("%Y"))
        doc_day, doc_month, doc_year = int(document.end_date.strftime("%d")), int(document.end_date.strftime("%m")), int(document.end_date.strftime("%Y"))
        
        if (new_year == doc_year) and (new_month >= doc_month) and (new_day > doc_day):
            movements = MovementOfDocument.objects.filter(document=document)
            for movement in movements:
                in_process += 1 if movement.status == 'In_process' else 0
                not_completed += 1 if movement.status == 'Not_completed' else 0
                done += 1 if movement.status == 'Done' else 0
            is_main_person = movements.get(is_main_person=True).status
            doc_status_was = document.status_v
            if (in_process <= done >= not_completed) and is_main_person == 'Done':
                document.status = 'Done'
            else:
                document.status = 'Not_completed'               
            messages.append(f'{count_}) Номер: {document.number} - Статус документа был: {doc_status_was} - Изменено: {document.status_v()}')
            document.save()
            create_check_list.delay(document.pk, document.author.pk, document.status)
            body = f'Отчет об обработке документа с номером {document.number}, истек срок документа.'\
                   f'Чтобы узнать подробно о документе нажмите на эту ссылку <br>'\
                   f'<a href="{document.get_absolute_url()}" class="btn btn-light px-3 mt-3 font-weight-bold" style="font-size: 16px">Подробно</a>'
            create_notification.delay('document', document.pk, document.author.pk, document.author.pk, body)
            count_ += 1
    messages.append(f'Всего обработано "{count_}" документов, обработка документов заняло {timezone.localtime() - date_now} времении')
    send_mail.delay('Отчет об обработке документов', 'adikgk@mail.ru', 'Адилет Эстебес уулу', messages)