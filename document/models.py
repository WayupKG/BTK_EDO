import os

from django.db import models
from django.db.models.query_utils import select_related_descend
from django.forms import widgets
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField

from .services import (
    STATUS, 
    STATUS_STATEMENT,
    REPLY_STATUS, 
    TYPE, PURPOSES, 
    APPOINTMENT, 
    create_notification,
    upload_to_reply_file, 
    upload_to_file, 
    create_number, 
    gen_slug
    )


class DocumentInProcessManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='In_process').order_by('-created')


class DocumentDoneManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='Done').order_by('-created')


class DocumentNotExecutedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='Not_completed').order_by('-created')


class MovementInProcessManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(document__status='In_process').order_by('-created')


class MovementDoneManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(document__status='Done').order_by('-created')


class MovementNotExecutedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(document__status='Not_completed').order_by('-created')


class Statement(models.Model):
    """Заявление и Рапорт"""
    number = models.CharField('Регистрационный номер', max_length=20, null=True, blank=True)
    author = models.ForeignKey('employee.Profile', verbose_name='Автор', on_delete=models.PROTECT, related_name='statements_author', null=True)
    type = models.CharField('Тип документа', max_length=20, choices=TYPE, default='Document')
    body = RichTextUploadingField('Описание документа')
    slug = models.SlugField(max_length=255, null=True, blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_STATEMENT, default='Submitted')
    director = models.ForeignKey('employee.Profile', verbose_name='Руководитель', on_delete=models.PROTECT, related_name='statements', null=True, blank=True)
    responsible = models.ForeignKey('employee.Profile', verbose_name='Ответственный', on_delete=models.PROTECT, related_name='statements_responsible', null=True, blank=True)
    
    is_editor_author = models.BooleanField(default=False)
    is_editor_director = models.BooleanField(default=True)
    is_editor_responsible = models.BooleanField(default=False)
    
    is_open_view_director = models.BooleanField(default=False)
    is_open_view_director_date = models.DateTimeField(null=True, blank=True)

    is_open_view_responsible = models.BooleanField(default=False)
    is_open_view_responsible_date = models.DateTimeField(null=True, blank=True)

    date_of_signing = models.DateTimeField(verbose_name='Дата подписания', blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
        
    def save(self, *args, **kwargs):
        super(Statement, self).save(*args, **kwargs)
        self.number = create_number(self.pk)
        self.slug = gen_slug(self.number, self.author.get_full_name())
        if self.status == 'Done':
            self.is_editor_author = False
            self.is_editor_director = False
            self.is_editor_responsible = False
        super(Statement, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail-doc-view', kwargs={'slug': self.slug})

    def get_pdf_url(self):
        return reverse('render-statement-pdf', kwargs={'slug': self.slug})

    def status_v(self):
        return dict(STATUS_STATEMENT)[self.status]

    def type_v(self):
        return dict(TYPE)[self.type]

    def __str__(self):
        return f'{self.number}-{self.author}'

    class Meta:
        ordering = ('-created',)
        db_table = 'Statement'
        verbose_name = 'Заявление и Рапорт'
        verbose_name_plural = 'Заявлении и Рапорты'


class MessageStatement(models.Model):
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE, related_name='messages')
    message = models.CharField(max_length=255)

    is_main = models.BooleanField(default=False)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.statement.author}-{self.message}'

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщении'


class Document(models.Model):
    """Документ"""
    number = models.CharField('Регистрационный номер', max_length=20, null=True, blank=True)
    author = models.ForeignKey('employee.Profile', verbose_name='Автор', on_delete=models.PROTECT, related_name='documents_author', null=True)
    name = models.CharField('Название документа', max_length=255)
    body = models.TextField('Описание документа')
    slug = models.SlugField()
    end_date = models.DateField(verbose_name='Срок исполнения', null=True, blank=True)
    purposes = models.CharField('Назначение', max_length=20, choices=PURPOSES, default='For_your_information')
    status = models.CharField('Статус', max_length=20, choices=STATUS, default='In_process')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    in_process = DocumentInProcessManager()
    done = DocumentDoneManager()
    not_executed = DocumentNotExecutedManager()
    
    def save(self, *args, **kwargs):
        super(Document, self).save(*args, **kwargs)
        self.number = create_number(self.pk)
        self.slug = gen_slug(self.number, self.name)[:40]
        super(Document, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail-shipped-view', kwargs={'slug': self.slug})

    def get_absolute_url_inbox(self):
        return reverse('detail-doc-view', kwargs={'slug': self.slug})

    def purposes_v(self):
        return dict(PURPOSES)[self.purposes]

    def status_v(self):
        return dict(STATUS)[self.status]

    def __str__(self):
        return f'{self.number}-{self.name}'

    class Meta:
        ordering = ('-created',)
        db_table = 'Document'
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'


class FileDocument(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='files')
    file = models.FileField('Файлы', upload_to=upload_to_file, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.document.number

    class Meta:
        ordering = ('created',)
        verbose_name = 'Файл документа'
        verbose_name_plural = 'Файлы документов'


class MovementOfDocument(models.Model):
    """Движение документа"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='movements')
    responsible = models.ForeignKey('employee.Profile', on_delete=models.PROTECT, related_name='movements')
    status = models.CharField('Статус документа', max_length=20, choices=STATUS, default='In_process')
    is_main_person = models.BooleanField('Ответственный сотрудник', default=False)
    is_redirect = models.BooleanField('Перенаправлен сотруднику', default=False)
    is_send_reply = models.BooleanField('Можеть ли этот сотрудник отправить ответ', default=True)
    open_view = models.BooleanField(default=False)
    datetime_view = models.DateTimeField(verbose_name='Дата и время просмотра', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    in_process = MovementInProcessManager()
    done = MovementDoneManager()
    not_executed = MovementNotExecutedManager()

    def status_v(self):
        return dict(STATUS)[self.status]

    def __str__(self):
        return f'Движение: {self.document.number}-{self.responsible}'

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Движение документа'
        verbose_name_plural = 'Движения документов'


class ReplyDocument(models.Model):
    """Ответ на документ"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='answers', null=True)
    movement = models.ForeignKey(MovementOfDocument, on_delete=models.CASCADE, related_name='answers')
    appointment = models.CharField('Движение', choices=APPOINTMENT, max_length=30, default='Waiting')
    status = models.CharField('Статус ответа', max_length=20, choices=REPLY_STATUS, default='Waiting')
    description = models.TextField('Описание', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if self.status == 'To_accept':
            self.movement.status = 'Done'
            self.movement.is_open_reply = False
            self.movement.save()
        super(ReplyDocument, self).save(*args, **kwargs)

    def status_v(self):
        return dict(STATUS)[self.status]

    def appointment_v(self):
        return dict(APPOINTMENT)[self.appointment]

    def __str__(self):
        return f'Ответ: {self.movement.document}'

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class FileReplyDocument(models.Model):
    movement = models.ForeignKey(MovementOfDocument, on_delete=models.CASCADE, related_name='answers_files', null=True)
    reply = models.ForeignKey(ReplyDocument, on_delete=models.CASCADE, related_name='files')
    file = models.FileField('Файл', upload_to=upload_to_reply_file)
    created = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return str(self.reply)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Файл ответа'
        verbose_name_plural = 'Файлы ответа'
