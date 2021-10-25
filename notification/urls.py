from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationView.as_view(), name='notification'),
    path('remove/<int:pk>/<int:obj_pk>/', views.remove_notification, name='remove_notification'),
    path('single/<int:pk>/<int:obj_pk>/', views.DetailNotificationView.as_view(), name='single_notification'),
]
