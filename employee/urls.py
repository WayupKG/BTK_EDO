from django.urls import path
from .views import Registration, profile_view

urlpatterns = [
    path('registration/', Registration.as_view(), name="registration"),
    path('profile/<username>/', profile_view, name="Profile"),
]
