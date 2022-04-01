from django.urls import path
from .views import (
    manager_view,

    benef_view,
    add_benef_view,
    edit_benef_view,

    merchant_view,
    add_merchant_view,
    edit_merchant_view,

    food_view,
    edit_food_view,

    donor_view,
    add_donor_view,
    edit_donor_view,
)

app_name = 'manager'
urlpatterns = [
    path('', manager_view, name='manager'),
    path('beneficiary', benef_view, name='benef'),
    path('beneficiary/add', add_benef_view, name='add_benef'),
    path('beneficiary/edit/<str:email>', edit_benef_view, name='edit_benef'),

    path('merchant', merchant_view, name='merchant'),
    path('merchant/add', add_merchant_view, name='add_merchant'),
    path('merchant/edit/<str:email>', edit_merchant_view, name='edit_merchant'),

    path('food', food_view, name='food'),
    path('food/edit/<str:food_sn>', edit_food_view, name='edit_food'),

    path('donor', donor_view, name='donor'),
    path('donor/add', add_donor_view, name='add_donor'),
    path('donor/edit/<str:email>', edit_donor_view, name='edit_donor'),
]