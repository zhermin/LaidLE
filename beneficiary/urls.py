from django.urls import path
from .views import beneficiary_view, profile_view, generated_coupon_view

app_name = 'beneficiary'
urlpatterns = [
    path('', beneficiary_view, name='beneficiary'),
    path('profile', profile_view, name='profile'),
    path('coupon/<str:coupon_sn>', generated_coupon_view, name='coupon'),
]