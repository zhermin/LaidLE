from django.shortcuts import render
from django.db import connection

# Create your views here.
def beneficiary_view(request):
    test_benef = 'kdeetch5@stumbleupon.com'

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(c.coupon_sn) AS coupon_count
                FROM coupon c, beneficiary b
                WHERE c.benef_email = b.benef_email
                AND b.benef_email = %(benef_email)s
                GROUP BY b.benef_email;
            """, {
                'benef_email': test_benef,
            })
            benef_coupon_count = cursor.fetchone()[0]
    except:
        benef_coupon_count = -1

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.food_sn, m.merchant_name, f.food_name, m.merchant_location
            FROM produced_by p, food f, merchant m, beneficiary b
            WHERE p.merchant_email = m.merchant_email
            AND p.food_sn = f.food_sn
            AND b.benef_email = %(benef_email)s
            ORDER BY m.merchant_location = b.benef_location DESC, m.merchant_location;
        """, {
            'benef_email': test_benef,
        })
        food_items = cursor.fetchall()

    context = {
        "benef_coupon_count": benef_coupon_count,
        "food_items": food_items
    }

    return render(request, "beneficiary/index.html", context)

def beneficiary_food_view(request, food_sn):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT food_sn, food_name, food_desc
            FROM food
            WHERE food_sn = %(food_sn)s;
        """, {
            'food_sn': food_sn,
        })
        food_item = cursor.fetchone()

    context = {
        "food_item": food_item
    }

    return render(request, "beneficiary/view.html", context)