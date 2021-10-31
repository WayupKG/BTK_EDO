from django.urls import path
from .views import Registration, ProfileView

urlpatterns = [
    path('registration/', Registration.as_view(), name="registration"),
    path('profile/<pk>/<username>/', ProfileView.as_view(), name="profile"),
]
