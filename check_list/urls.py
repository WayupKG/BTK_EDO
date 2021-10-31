from django.urls import path
from . import views

urlpatterns = [
    path('', views.CheckListView.as_view(), name="check_list"),
    path('remove/pdf-<str:key>/', views.remove_check_list, name="remove_check_list_pdf"),
    path('pdf-<str:key>/', views.CheckListPDFView.as_view(), name="check_list_pdf"),
]
