import time

from django.utils import timezone
from core.celery import app
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from employee.models import User
from document.models import Document
from check_list.models import CheckList


@app.task
def send_register_mail(email, password, last_name, first_name):
    title, from_email, to = settings.EMAIL_TITLE_FROM, settings.EMAIL_HOST_USER, email
    to_form, headers = f'{last_name} {first_name} <{to}>', {'From': f'{title} <{from_email}>'}
    html_content = render_to_string('Email/send_register_mail.html', {'user': f'{last_name} {first_name}', 
                                                                 'email': email, 'pass': password})  
    text_content = strip_tags(html_content)  

    msg = EmailMultiAlternatives('Регистрация в электронном документообороте "EDO_BTK"', text_content, from_email, [to_form], headers=headers)
    msg.attach_alternative(html_content, "text/html")
    # msg.attach_file('static/images/EDOBTK.svg')
    msg.send(fail_silently=False)



@app.task
def create_check_list(document_id):
    doc = Document.objects.get(pk=document_id)
    update_redirect, create_redirect = CheckList.objects.get_or_create(document=doc, defaults={'document': doc})
    if not create_redirect:
        update_redirect.document = doc
        update_redirect.save()
