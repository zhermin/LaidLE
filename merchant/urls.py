from django.urls import path
from .views import merchant_view, add_food_view, edit_food_view

app_name = 'merchant'
urlpatterns = [
    path('', merchant_view, name='merchant'),
    path('food/add', add_food_view, name='add_food'),
    path('food/edit/<str:food_sn>', edit_food_view, name='edit_food'),
]