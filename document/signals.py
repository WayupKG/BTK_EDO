from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from .models import Document


# @receiver(post_save, sender=Document)
# def update_number_doc(sender, instance, **kwargs):
#     print(instance.id)


# create_number = Signal(providing_args=["id"])