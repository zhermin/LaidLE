from django.shortcuts import render, redirect
from django.db import IntegrityError, connection
from django.contrib import messages
from account.decorators import check_permissions

# Create your views here.
@check_permissions('beneficiary')
def beneficiary_view(request):

    if request.POST:
        if request.POST['action'] == 'claim':
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO claim (coupon_sn, benef_email, merchant_email, food_sn)
                        VALUES (%(coupon_sn)s, %(benef_email)s, %(merchant_email)s, %(food_sn)s);
                    """, {
                        'coupon_sn': request.POST['coupon_sn'],
                        'benef_email': request.session['email'],
                        'merchant_email': request.POST['merchant_email'],
                        'food_sn': request.POST['food_sn'],
                    })
                    messages.add_message(request, messages.SUCCESS, 'Coupon claimed successfully!')
                    return redirect(f'coupon/{request.POST["coupon_sn"]}')

            except IntegrityError:
                messages.add_message(request, messages.ERROR, 'Error claiming coupon! Check if you have sufficient coupons.')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.coupon_sn, c.issue_date, c.expiry_date
            FROM coupon c, beneficiary b
            WHERE c.benef_email = b.email
            AND b.email = %(email)s
            AND c.expiry_date >= NOW()
            AND NOT EXISTS (
                SELECT
                FROM claim cl
                WHERE cl.coupon_sn = c.coupon_sn
            )
            ORDER BY c.issue_date;
        """, {
            'email': request.session['email'],
        })
        coupons = cursor.fetchall()
        coupon_count = len(coupons)
        request.session.coupon_count = coupon_count

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

@check_permissions('beneficiary')
def profile_view(request):
    return render(request, 'account/profile.html')

@check_permissions('beneficiary')
def generated_coupon_view(request, coupon_sn):

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cl.coupon_sn, cl.claim_date, m.location, f.food_name, f.food_desc
                FROM claim cl, beneficiary b, food f, merchant m
                WHERE cl.benef_email = b.email
                AND b.email = %(email)s
                AND cl.coupon_sn = %(coupon_sn)s
                AND cl.food_sn = f.food_sn
                AND f.merchant_email = m.email;
            """, {
                'email': request.session['email'],
                'coupon_sn': coupon_sn,
            })
            coupon = cursor.fetchone()
    except IntegrityError:
        messages.add_message(request, messages.ERROR, 'Error claiming coupon! Check if you have sufficient coupons.')

    context = {
        "coupon": coupon
    }

    return render(request, 'beneficiary/coupon.html', context)