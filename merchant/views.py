from django.shortcuts import render, redirect
from django.db import IntegrityError, connection
from django.contrib import messages
from account.decorators import check_permissions

# Create your views here.
@check_permissions('merchant')
def merchant_view(request):

    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM food WHERE food_sn = %(food_sn)s;
                """, {
                    'food_sn': request.POST['food_sn'],
                })
                messages.add_message(request, messages.WARNING, 'Food item deleted successfully!')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT m.location, f.food_sn, f.food_name, p.name, f.food_desc
            FROM person p, food f, merchant m
            WHERE p.email = m.email
            AND m.email = f.merchant_email
            AND m.email = %(email)s
            ORDER BY f.food_name;
        """, {
            'email': request.session['email'],
        })
        food_items = cursor.fetchall()

    context = {
        "food_items": food_items
    }

    return render(request, 'merchant/index.html', context)

@check_permissions('merchant')
def profile_view(request):

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

                messages.add_message(request, messages.SUCCESS, 'Profile updated successfully!')
                request.session['name'] = request.POST['name']
                request.session['email'] = request.POST['email']
                return redirect(f"/{request.session['role']}")

        except (IntegrityError) as e:
            messages.add_message(request, messages.ERROR, "One or more fields are invalid.")

    return render(request, 'account/profile.html')

@check_permissions('merchant')
def add_food_view(request):

    if request.POST:
        try:
            with connection.cursor() as cursor:

                cursor.execute("""
                    INSERT INTO food (merchant_email, food_name, food_desc)
                    VALUES (%(merchant_email)s, %(food_name)s, %(food_desc)s);
                """, {
                    'merchant_email': request.session['email'],
                    'food_name': request.POST['food_name'],
                    'food_desc': request.POST['food_desc'],
                })

                messages.add_message(request, messages.SUCCESS, 'Food item added successfully!')
                return redirect('merchant:merchant')
        except IntegrityError as e:
            messages.add_message(request, messages.ERROR, 'One or more fields are invalid.')

    return render(request, 'merchant/add.html')

@check_permissions('merchant')
def edit_food_view(request, food_sn):

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM food WHERE food_sn = %(food_sn)s
        """, {
            'food_sn': food_sn,
        })
        food_item = cursor.fetchone()

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

            cursor.execute("""
                SELECT * FROM food WHERE food_sn = %(food_sn)s
            """, {
                'food_sn': request.POST['food_sn'],
            })
            food_item = cursor.fetchone()
            messages.add_message(request, messages.SUCCESS, 'Food item updated successfully!')

    context = {
        "food_item": food_item,
    }

    return render(request, 'merchant/edit.html', context)