import random

from django.db import models
from document.services import STATUS


class CheckList(models.Model):
    document = models.OneToOneField('document.Document', on_delete=models.PROTECT, related_name='check_lists')
    author = models.ForeignKey('employee.Profile', on_delete=models.CASCADE, related_name='check_lists', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, null=True, blank=True)
    private_key = models.CharField(max_length=180, default=0)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        chars = 'abcd465efgh7ijk5lno4165pqrs7t1234dfhh4gdfsjk456saad5ad6489fghfgfhuv8wx9yz12378440'
        key = ''
        for i in range(20):
            key += random.choice(chars)
        self.private_key = key
        self.author = self.document.author
        self.status = self.document.status
        super(CheckList, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Чек лист'
        verbose_name_plural = 'Чек листы'
