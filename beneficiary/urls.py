from django.urls import path
from .views import beneficiary_view

app_name = 'beneficiary'
urlpatterns = [
    path('', beneficiary_view, name='beneficiary'),
]