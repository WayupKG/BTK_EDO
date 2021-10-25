from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="Home"),
    path('address/book/', views.AddressBookView.as_view(), name="address_book"),
]
