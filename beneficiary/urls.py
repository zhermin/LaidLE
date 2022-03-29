from django.urls import path
from .views import beneficiary_view, beneficiary_food_view

app_name = 'beneficiary'
urlpatterns = [
    path('', beneficiary_view, name='beneficiary'),
    path('food/<str:food_sn>', beneficiary_food_view, name='food'),
]