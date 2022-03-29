from django.urls import path
from .views import merchant_view, merchant_food_view, add_food_view, edit_food_view

app_name = 'merchant'
urlpatterns = [
    path('', merchant_view, name='merchant'),
    path('food/add', add_food_view, name='add_food'),
    path('food/<str:food_sn>', merchant_food_view, name='food'),
    path('food/<str:food_sn>/edit', edit_food_view, name='edit_food'),
]