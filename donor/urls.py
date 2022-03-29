from django.urls import path
from .views import donor_view

app_name = 'donor'
urlpatterns = [
    path('', donor_view, name='donor'),
]