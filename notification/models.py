from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Notification(models.Model):
    """Уведомление"""
    TYPE = (
        ('statement', 'заявление/рапорт'),
        ('document', 'документ'),
        ('movement', 'движение'),
        ('reply', 'ответ'),
        ('checklist', 'чеклист'),
        ('other', 'Другое'),
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='notifications')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    body = models.TextField('Описания')
    user = models.ForeignKey('employee.Profile', on_delete=models.CASCADE, related_name='notifications')
    open_view = models.BooleanField(default=False)
    datetime_view = models.DateTimeField(verbose_name='Дата и время просмотра', null=True, blank=True)
    type = models.CharField('Type', max_length=20, choices=TYPE, default='document', null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.content_object}-{self.body}'

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомлении'

