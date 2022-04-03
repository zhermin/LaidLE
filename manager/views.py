from django.shortcuts import render, redirect
from django.db import IntegrityError, DataError, connection
from django.contrib import messages
from django.core.paginator import Paginator
from account.decorators import check_permissions

# Main View, Shows Donations
@check_permissions('manager')
def manager_view(request):

    if request.POST:
        if request.POST['action'] == 'allocate':
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO coupon (issue_date, expiry_date, benef_email)
                    SELECT	DATE_TRUNC('MONTH', f.year_month + INTERVAL '1 MONTH') AS issue_date,
                            DATE_TRUNC('MONTH', f.year_month + INTERVAL '2 MONTH') AS expiry_date,
                            benef_email
                    FROM fund_view f
                    CROSS JOIN LATERAL (
                        SELECT b.email AS benef_email
                        FROM beneficiary b LEFT JOIN coupon c
                        ON b.email = c.benef_email
                        GROUP BY b.email, b.household_income, f.year_month
                        HAVING f.year_month = DATE_TRUNC('MONTH', NOW() - INTERVAL '1 month')
                        ORDER BY COUNT(c.benef_email), b.household_income
                        LIMIT f.quotient
                    ) AS benef_email;
                """)

                messages.add_message(request, messages.SUCCESS, 'Coupons allocated to beneficiaries successfully!')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM donation
            ORDER BY donation_date DESC;
        """)
        donations_paginator = Paginator(cursor.fetchall(), 10)
        donations_page = request.GET.get('page')
        donations = donations_paginator.get_page(donations_page)

    context = {
        "donations": donations,
    }

    return render(request, "manager/manager_base.html", context)

@check_permissions('manager')
def profile_view(request):
    return render(request, 'account/profile.html')

# Beneficiary Views
@check_permissions('manager')
def benef_view(request):

    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM person
                    WHERE email = %(email)s;
                """, {
                    'email': request.POST['email']
                })

            messages.add_message(request, messages.SUCCESS, 'Beneficiary deleted successfully!')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.name, p.email, b.household_income, b.location
            FROM person p, beneficiary b
            WHERE p.email = b.email
            ORDER BY p.name;
        """)
        beneficiaries_paginator = Paginator(cursor.fetchall(), 5)
        beneficiaries_page = request.GET.get('page')
        beneficiaries = beneficiaries_paginator.get_page(beneficiaries_page)

    context = {
        "beneficiaries": beneficiaries
    }

    return render(request, "manager/beneficiary/index.html", context)

@check_permissions('manager')
def add_benef_view(request):

    if request.POST:
        try:
            with connection.cursor() as cursor:
                # add new entry to both generalized and specialized tables using data modifying CTE
                cursor.execute("""
                    WITH data AS (
                        INSERT INTO person (name, email, password, role)
                        VALUES (
                            %(name)s,
                            %(email)s,
                            crypt(%(password)s, gen_salt('bf')),
                            'beneficiary'
                        ) RETURNING email
                    )
                    INSERT INTO beneficiary (email, household_income, location)
                    VALUES (
                        (SELECT email FROM data),
                        %(household_income)s,
                        %(location)s
                    );
                """, {
                    'name': request.POST['name'],
                    'email': request.POST['email'],
                    'password': request.POST['password'],
                    'household_income': request.POST['household_income'],
                    'location': request.POST['location'],
                })

                messages.add_message(request, messages.SUCCESS, 'Beneficiary added successfully!')
                return redirect('/manager/beneficiary')

        except (IntegrityError, DataError) as e:
            messages.add_message(request, messages.ERROR, "One or more fields are invalid.")

    return render(request, "manager/beneficiary/add.html")

@check_permissions('manager')
def edit_benef_view(request, email):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.name, p.email, b.household_income, b.location
            FROM person p, beneficiary b
            WHERE p.email = b.email
            AND p.email = %(email)s;
        """, {
            'email': email
        })
        beneficiary = cursor.fetchone()

    if request.POST:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    WITH data AS (
                        UPDATE person
                        SET name = %(name)s,
                            email = %(email)s,
                            password = crypt(%(password)s, gen_salt('bf'))
                        WHERE email = %(old_email)s
                        RETURNING email
                    )
                    UPDATE beneficiary
                    SET email = (SELECT email FROM data),
                        household_income = %(household_income)s,
                        location = %(location)s
                    WHERE email = (SELECT email FROM data);
                """, {
                    'old_email': request.POST['old_email'],
                    'name': request.POST['name'],
                    'email': request.POST['email'],
                    'password': request.POST['password'],
                    'household_income': request.POST['household_income'],
                    'location': request.POST['location'],
                })

                messages.add_message(request, messages.SUCCESS, 'Beneficiary updated successfully!')
                return redirect('/manager/beneficiary')

        except (IntegrityError, DataError) as e:
            messages.add_message(request, messages.ERROR, "One or more fields are invalid.")

    context = {
        "beneficiary": beneficiary
    }

    return render(request, "manager/beneficiary/edit.html", context)

# Merchant Views
@check_permissions('manager')
def merchant_view(request):

    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM person
                    WHERE email = %(email)s;
                """, {
                    'email': request.POST['email']
                })

            messages.add_message(request, messages.SUCCESS, 'Merchant deleted successfully!')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.name, p.email, m.location
            FROM person p, merchant m
            WHERE p.email = m.email
            AND p.email <> 'anonymous_merchant'
            ORDER BY p.name;
        """)
        merchants_paginator = Paginator(cursor.fetchall(), 5)
        merchants_page = request.GET.get('page')
        merchants = merchants_paginator.get_page(merchants_page)

    context = {
        "merchants": merchants
    }

    return render(request, "manager/merchant/index.html", context)

@check_permissions('manager')
def add_merchant_view(request):

    if request.POST:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    WITH data AS (
                        INSERT INTO person (name, email, password, role)
                        VALUES (
                            %(name)s,
                            %(email)s,
                            crypt(%(password)s, gen_salt('bf')),
                            'merchant'
                        ) RETURNING email
                    )
                    INSERT INTO merchant (email, location)
                    VALUES (
                        (SELECT email FROM data),
                        %(location)s
                    );
                """, {
                    'name': request.POST['name'],
                    'email': request.POST['email'],
                    'password': request.POST['password'],
                    'location': request.POST['location'],
                })

                messages.add_message(request, messages.SUCCESS, 'Merchant added successfully!')
                return redirect('/manager/merchant')

        except (IntegrityError, DataError) as e:
            messages.add_message(request, messages.ERROR, "One or more fields are invalid.")

    return render(request, "manager/merchant/add.html")

@check_permissions('manager')
def edit_merchant_view(request, email):

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.name, p.email, m.location
                FROM person p, merchant m
                WHERE p.email = m.email
                AND p.email = %(email)s;
            """, {
                'email': email
            })
            merchant = cursor.fetchone()

        if request.POST:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        WITH data AS (
                            UPDATE person
                            SET name = %(name)s,
                                email = %(email)s,
                                password = crypt(%(password)s, gen_salt('bf'))
                            WHERE email = %(old_email)s
                            RETURNING email
                        )
                        UPDATE merchant
                        SET email = (SELECT email FROM data),
                            location = %(location)s
                        WHERE email = (SELECT email FROM data);
                    """, {
                        'old_email': request.POST['old_email'],
                        'name': request.POST['name'],
                        'email': request.POST['email'],
                        'password': request.POST['password'],
                        'location': request.POST['location'],
                    })

                    messages.add_message(request, messages.SUCCESS, 'Merchant updated successfully!')
                    return redirect('/manager/merchant')

            except (IntegrityError, DataError) as e:
                messages.add_message(request, messages.ERROR, "One or more fields are invalid.")

        context = {
            "merchant": merchant
        }

        return render(request, "manager/merchant/edit.html", context)

# Merchant's Food Views
@check_permissions('manager')
def food_view(request):

    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM food
                    WHERE food_sn = %(food_sn)s;
                """, {
                    'food_sn': request.POST['food_sn']
                })

            messages.add_message(request, messages.SUCCESS, 'Food item deleted successfully!')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT food_sn, merchant_email, food_name, food_desc
            FROM food f
            ORDER BY merchant_email;
        """)
        food_items_paginator = Paginator(cursor.fetchall(), 5)
        food_items_page = request.GET.get('page')
        food_items = food_items_paginator.get_page(food_items_page)

    context = {
        "food_items": food_items
    }

    return render(request, "manager/food/index.html", context)

@check_permissions('manager')
def edit_food_view(request, food_sn):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT food_sn, merchant_email, food_name, food_desc
            FROM food
            WHERE food_sn = %(food_sn)s;
        """, {
            'food_sn': food_sn
        })
        food_item = cursor.fetchone()

    if request.POST:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE food
                    SET food_name = %(food_name)s,
                        food_desc = %(food_desc)s
                    WHERE food_sn = %(food_sn)s;
                """, {
                    'food_name': request.POST['food_name'],
                    'food_desc': request.POST['food_desc'],
                    'food_sn': food_sn
                })

                messages.add_message(request, messages.SUCCESS, 'Food item updated successfully!')
                return redirect('/manager/food')

        except (IntegrityError, DataError) as e:
            messages.add_message(request, messages.ERROR, "One or more fields are invalid.")

    context = {
        "food_item": food_item
    }

    return render(request, "manager/food/edit.html", context)

# Donor Views
@check_permissions('manager')
def donor_view(request):

    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM person
                    WHERE email = %(email)s;
                """, {
                    'email': request.POST['email']
                })

            messages.add_message(request, messages.SUCCESS, 'Donor deleted successfully!')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.name, p.email, d.coin
            FROM person p, donor d
            WHERE p.email = d.email
            AND p.email <> 'anonymous_donor'
            ORDER BY p.name;
        """)
        donors_paginator = Paginator(cursor.fetchall(), 5)
        donors_page = request.GET.get('page')
        donors = donors_paginator.get_page(donors_page)

    context = {
        "donors": donors
    }

    return render(request, "manager/donor/index.html", context)

@check_permissions('manager')
def add_donor_view(request):

    if request.POST:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    WITH data AS (
                        INSERT INTO person (name, email, password, role)
                        VALUES (
                            %(name)s,
                            %(email)s,
                            crypt(%(password)s, gen_salt('bf')),
                            'donor'
                        ) RETURNING email
                    )
                    INSERT INTO donor (email)
                    VALUES (
                        (SELECT email FROM data)
                    );
                """, {
                    'name': request.POST['name'],
                    'email': request.POST['email'],
                    'password': request.POST['password'],
                })

                messages.add_message(request, messages.SUCCESS, 'Donor added successfully!')
                return redirect('/manager/donor')

        except (IntegrityError, DataError) as e:
            messages.add_message(request, messages.ERROR, "One or more fields are invalid.")

    return render(request, "manager/donor/add.html")

@check_permissions('manager')
def edit_donor_view(request, email):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.name, p.email
            FROM person p
            WHERE p.email = %(email)s;
        """, {
            'email': email
        })
        donor = cursor.fetchone()

    if request.POST:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    WITH data AS (
                        UPDATE person
                        SET name = %(name)s,
                            email = %(email)s,
                            password = crypt(%(password)s, gen_salt('bf'))
                        WHERE email = %(old_email)s
                        RETURNING email
                    )
                    UPDATE donor
                    SET email = (SELECT email FROM data)
                    WHERE email = (SELECT email FROM data);
                """, {
                    'old_email': request.POST['old_email'],
                    'name': request.POST['name'],
                    'email': request.POST['email'],
                    'password': request.POST['password'],
                })

                messages.add_message(request, messages.SUCCESS, 'Donor updated successfully!')
                return redirect('/manager/donor')

        except (IntegrityError, DataError) as e:
            messages.add_message(request, messages.ERROR, "One or more fields are invalid.")

    context = {
        "donor": donor
    }

    return render(request, "manager/donor/edit.html", context)

# Coupon Views
@check_permissions('manager')
def coupon_view(request):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT coupon_sn, issue_date, expiry_date, benef_email
            FROM coupon
            ORDER BY issue_date DESC, benef_email;
        """)
        coupons_paginator = Paginator(cursor.fetchall(), 5)
        coupons_page = request.GET.get('page')
        coupons = coupons_paginator.get_page(coupons_page)

    context = {
        "coupons": coupons
    }

    return render(request, "manager/coupon/index.html", context)

# Claim Views
@check_permissions('manager')
def claim_view(request):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT coupon_sn, food_sn, claim_date, benef_email, merchant_email
            FROM claim
            ORDER BY claim_date DESC, benef_email;
        """)
        claims_paginator = Paginator(cursor.fetchall(), 5)
        claims_page = request.GET.get('page')
        claims = claims_paginator.get_page(claims_page)

    context = {
        "claims": claims
    }

    return render(request, "manager/claim/index.html", context)

# Reward Views
@check_permissions('manager')
def reward_view(request):

    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM reward
                    WHERE reward_sn = %(reward_sn)s;
                """, {
                    'reward_sn': request.POST['reward_sn']
                })

                messages.add_message(request, messages.SUCCESS, 'Reward deleted successfully!')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT reward_sn, reward_name, reward_desc, reward_price, reward_qty
            FROM reward
            ORDER BY reward_name;
        """)
        rewards_paginator = Paginator(cursor.fetchall(), 5)
        rewards_page = request.GET.get('page')
        rewards = rewards_paginator.get_page(rewards_page)

    context = {
        "rewards": rewards
    }

    return render(request, "manager/reward/index.html", context)

@check_permissions('manager')
def add_reward_view(request):

    if request.POST:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO reward (reward_name, reward_desc, reward_price, reward_qty)
                    VALUES (%(reward_name)s, %(reward_desc)s, %(reward_price)s, %(reward_qty)s)
                """, {
                    'reward_name': request.POST['reward_name'],
                    'reward_desc': request.POST['reward_desc'],
                    'reward_price': request.POST['reward_price'],
                    'reward_qty': request.POST['reward_qty'],
                })

                messages.add_message(request, messages.SUCCESS, 'Reward added successfully!')
                return redirect('/manager/reward')

        except (IntegrityError, DataError) as e:
            messages.add_message(request, messages.ERROR, "One or more fields are invalid.")

    return render(request, "manager/reward/add.html")

@check_permissions('manager')
def edit_reward_view(request, reward_sn):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT reward_sn, reward_name, reward_price, reward_qty, reward_desc
            FROM reward
            WHERE reward_sn = %(reward_sn)s;
        """, {
            'reward_sn': reward_sn
        })
        reward = cursor.fetchone()

    if request.POST:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE reward
                    SET reward_name = %(reward_name)s,
                        reward_desc = %(reward_desc)s,
                        reward_price = %(reward_price)s,
                        reward_qty = %(reward_qty)s
                    WHERE reward_sn = %(reward_sn)s;
                """, {
                    'reward_sn': request.POST['reward_sn'],
                    'reward_name': request.POST['reward_name'],
                    'reward_desc': request.POST['reward_desc'],
                    'reward_price': request.POST['reward_price'],
                    'reward_qty': request.POST['reward_qty'],
                })

                messages.add_message(request, messages.SUCCESS, 'Reward updated successfully!')
                return redirect('/manager/reward')

        except (IntegrityError, DataError) as e:
            messages.add_message(request, messages.ERROR, "One or more fields are invalid.")

    context = {
        "reward": reward
    }

    return render(request, "manager/reward/edit.html", context)

@check_permissions('manager')
def redemption_view(request):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rd.reward_sn, rw.reward_name, rd.redeem_date, rd.donor_email
            FROM redemption rd, reward rw
            WHERE rd.reward_sn = rw.reward_sn
            ORDER BY redeem_date DESC, donor_email;
        """)
        redemptions_paginator = Paginator(cursor.fetchall(), 5)
        redemptions_page = request.GET.get('page')
        redemptions = redemptions_paginator.get_page(redemptions_page)

    context = {
        "redemptions": redemptions
    }

    return render(request, "manager/redemption/index.html", context)