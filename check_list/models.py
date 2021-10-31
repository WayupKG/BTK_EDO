import random
from cryptography.fernet import Fernet
from django.db import models
from document.services import STATUS


class CheckList(models.Model):
    document = models.OneToOneField('document.Document', on_delete=models.PROTECT, related_name='check_lists')
    author = models.ForeignKey('employee.Profile', on_delete=models.CASCADE, related_name='check_lists')
    status = models.CharField(max_length=20)
    private_key = models.CharField(max_length=180, default=0, null=True, blank=True)
    open_view = models.BooleanField(default=False)
    datetime_view = models.DateTimeField(verbose_name='Дата и время просмотра', null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.private_key:
            self.private_key = Fernet.generate_key()[::3]
        super(CheckList, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Чек лист'
        verbose_name_plural = 'Чек листы'
