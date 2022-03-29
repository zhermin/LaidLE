from django.shortcuts import render, redirect
from django.db import connection

# Create your views here.
def manager_view(request):

    with connection.cursor() as cursor:
        # get all beneficiaries
        cursor.execute("""
            SELECT * FROM beneficiary
            ORDER BY benef_name;
        """)
        beneficiaries = cursor.fetchall()

        # get all merchants
        cursor.execute("""
            SELECT * FROM merchant
            ORDER BY merchant_email;
        """)
        merchants = cursor.fetchall()

        # get all merchants' food items
        cursor.execute("""
            SELECT f.food_sn, m.merchant_email, f.food_name, f.food_desc
            FROM produced_by p, food f, merchant m
            WHERE p.merchant_email = m.merchant_email
            AND p.food_sn = f.food_sn
            ORDER BY m.merchant_email;
        """)
        food_items = cursor.fetchall()

        # get all donors except anonymous
        cursor.execute("""
            SELECT * FROM donor
            WHERE donor_name <> 'anonymous'
            ORDER BY donor_name;
        """)
        donors = cursor.fetchall()

    context = {
        "beneficiaries": beneficiaries,
        "merchants": merchants,
        "food_items": food_items,
        "donors": donors
    }

    return render(request, "manager/index.html", context)

def add_benef_view(request):

    if request.POST:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO beneficiary (benef_name, benef_email, benef_pw, household_income, benef_location)
                VALUES (
                    %(benef_name)s, 
                    %(benef_email)s, 
                    crypt(%(benef_pw)s, gen_salt('bf'))
                    %(household_income)s,
                    %(benef_location)s
                );
            """, {
                'benef_name': request.POST['name'],
                'benef_email': request.POST['email'],
                'benef_pw': request.POST['password'],
            })

        return redirect('manager:manager')

    return render(request, "manager/beneficiary/add_beneficiary.html")

def add_merchant_view(request):

    if request.POST:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO merchant (merchant_name, merchant_email, merchant_pw, merchant_location)
                VALUES (
                    %(merchant_name)s, 
                    %(merchant_email)s, 
                    crypt(%(merchant_pw)s, gen_salt('bf')), 
                    %(merchant_location)s
                );
            """, {
                'merchant_name': request.POST['name'],
                'merchant_email': request.POST['email'],
                'merchant_pw': request.POST['password'],
                'merchant_location': request.POST['location'],
            })

        return redirect('manager:manager')

    return render(request, "manager/merchant/add_merchant.html")

def add_donor_view(request):

    if request.POST:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO donor (donor_name, donor_email, donor_pw)
                VALUES (%(donor_name)s, %(donor_email)s, crypt(%(donor_pw)s, gen_salt('bf')));
            """, {
                'donor_name': request.POST['name'],
                'donor_email': request.POST['email'],
                'donor_pw': request.POST['password'],
            })

        return redirect('manager:manager')

    return render(request, "manager/donor/add_donor.html")