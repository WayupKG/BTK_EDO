import time

from django.utils import timezone
from core.celery import app
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from document.models import Document
from check_list.models import CheckList


@app.task
def send_mail(title_send: str, email, full_name, body: list):
    title, from_email = settings.EMAIL_TITLE_FROM, settings.EMAIL_HOST_USER
    to_form, headers = f'{full_name} <{email}>', {'From': f'{title} <{from_email}>'}
    html_content = render_to_string('Email/send_mail.html', {'full_name': full_name, 'body': body })  
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(title_send, text_content, from_email, [to_form], headers=headers)
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)