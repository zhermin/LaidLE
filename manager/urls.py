from django.urls import path
from .views import manager_view, add_benef_view, add_merchant_view, add_donor_view

app_name = 'manager'
urlpatterns = [
    path('', manager_view, name='manager'),
    path('add/beneficiary', add_benef_view, name='add_benef'),
    path('add/merchant', add_merchant_view, name='add_merchant'),
    path('add/donor', add_donor_view, name='add_donor'),
]