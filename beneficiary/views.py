from django.shortcuts import render
from django.db import connection

# Create your views here.
def beneficiary_view(request):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.coupon_sn, c.issue_date, c.expiry_date
            FROM coupon c, beneficiary b
            WHERE c.benef_email = b.email
            AND b.email = %(email)s
            ORDER BY c.issue_date;
        """, {
            'email': request.session['email'],
        })
        coupons = cursor.fetchall()
        coupon_count = len(coupons)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT m.location, f.food_sn, f.food_name, p.name, f.food_desc
            FROM food f, person p, merchant m, beneficiary b
            WHERE p.email = m.email
            AND f.merchant_email = m.email
            AND b.email = %(email)s
            AND m.location = b.location
            ORDER BY p.name;
        """, {
            'email': request.session['email'],
        })
        food_items_near = cursor.fetchall()

        cursor.execute("""
            SELECT m.location, f.food_sn, f.food_name, p.name, f.food_desc
            FROM food f, person p, merchant m, beneficiary b
            WHERE p.email = m.email
            AND f.merchant_email = m.email
            AND b.email = %(email)s
            AND m.location <> b.location
            ORDER BY m.location, p.name;
        """, {
            'email': request.session['email'],
        })
        food_items_far = cursor.fetchall()

    context = {
        "coupons": coupons,
        "coupon_count": coupon_count,
        "food_items_near": food_items_near,
        "food_items_far": food_items_far,
    }

    return render(request, "beneficiary/index.html", context)