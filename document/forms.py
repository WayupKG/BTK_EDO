from django.forms import ModelForm, Select, Textarea, TextInput, DateInput, FileInput
from django.utils import timezone

from ckeditor_uploader.fields import RichTextUploadingField
from .models import *
from datetime import timedelta


class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class CreateDocumentForm(BaseForm):
    class Meta:
        model = Document
        fields = ['name', 'body', 'end_date', 'purposes']
        widgets = {
            'end_date': DateInput(attrs={'type': 'date', 'onload': 'validDate()', 'required': ''}),
        }


class CreateStatementRaportForm(BaseForm):
    class Meta:
        model = Statement
        fields = ['body']