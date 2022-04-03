from django.urls import path
from .views import donor_view, profile_view, generated_reward_view

app_name = 'donor'
urlpatterns = [
    path('', donor_view, name='donor'),
    path('profile', profile_view, name='profile'),
    path('reward/<str:reward_sn>', generated_reward_view, name='reward'),
]