from django.shortcuts import render, redirect
from django.db import connection
import uuid

# Create your views here.
test_merchant = 'malaysian@google.com.au'

def merchant_view(request):

    status = ''

    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM food WHERE food_sn = %(food_sn)s;
                """, {
                    'food_sn': request.POST['food_sn'],
                })
                status = 'Food item deleted successfully!'

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.food_sn, f.food_name, f.food_desc
            FROM produced_by p, food f, merchant m
            WHERE p.merchant_email = m.merchant_email
            AND p.food_sn = f.food_sn
            AND m.merchant_email = %(merchant_email)s;
        """, {
            'merchant_email': test_merchant,
        })
        food_items = cursor.fetchall()

    context = {
        "status": status,
        "food_items": food_items
    }

    return render(request, 'merchant/index.html', context)

def merchant_food_view(request, food_sn):

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

    return render(request, 'merchant/view.html', context)

def add_food_view(request):

    if request.POST:
        with connection.cursor() as cursor:
            new_uuid = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO food (food_sn, food_name, food_desc)
                VALUES (%(food_sn)s, %(food_name)s, %(food_desc)s);
            """, {
                'food_sn': new_uuid,
                'food_name': request.POST['food_name'],
                'food_desc': request.POST['food_desc'],
            })

            cursor.execute("""
                INSERT INTO produced_by (food_sn, merchant_email)
                VALUES (%(food_sn)s, %(merchant_email)s);
            """, {
                'food_sn': new_uuid,
                'merchant_email': test_merchant,
            })

            return redirect('merchant:merchant')

    return render(request, 'merchant/add.html')

def edit_food_view(request, food_sn):

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM food WHERE food_sn = %(food_sn)s
        """, {
            'food_sn': food_sn,
        })
        food_item = cursor.fetchone()

    status = ''

    if request.POST:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE food
                SET food_name = %(food_name)s, food_desc = %(food_desc)s
                WHERE food_sn = %(food_sn)s;
            """, {
                'food_sn': request.POST['food_sn'],
                'food_name': request.POST['food_name'],
                'food_desc': request.POST['food_desc'],
            })
            status = 'Food item edited successfully!'

            cursor.execute("""
                SELECT * FROM food WHERE food_sn = %(food_sn)s
            """, {
                'food_sn': request.POST['food_sn'],
            })
            food_item = cursor.fetchone()

    context = {
        "status": status,
        "food_item": food_item,
    }

    return render(request, 'merchant/edit.html', context)