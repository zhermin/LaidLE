from django.shortcuts import render, redirect
from django.db import IntegrityError, connection
from django.contrib import messages

# Create your views here.
def login_view(request):

    if request.POST:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name, email, role, pic
                FROM person
                WHERE email <> 'anonymous_donor'
                AND email <> 'anoymous_merchant'
                AND email = %(email)s
                AND password = crypt(%(password)s, password);
            """, {
                'email': request.POST['email'],
                'password': request.POST['password'],
            })
            person = cursor.fetchone()

            if person:
                request.session['name'] = person[0]
                request.session['email'] = person[1]
                request.session['role'] = person[2]
                request.session['pic'] = person[3]
                return redirect(f'/{person[2]}')
            else:
                messages.add_message(request, messages.ERROR, 'Invalid email or password.')

    return render(request, 'account/login.html')

def logout_view(request):

    if 'role' in request.session:
        request.session.flush()
    return redirect('/')

def signup_view(request):

    if request.POST:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT email, role FROM person
                    WHERE email <> 'anonymous_donor'
                    AND email <> 'anoymous_merchant'
                    AND email = %(email)s;
                """, {
                    'email': request.POST['email'],
                })
                person = cursor.fetchone()

                if person:
                    messages.add_message(
                        request, 
                        messages.ERROR, 
                        f'Oops! Email already registered as a {person[1]}. Please use a different email.'
                    )
                else:
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

                    messages.add_message(request, messages.SUCCESS, 'Registration successful!')
                    return redirect('login')

        except IntegrityError as e:
            messages.add_message(request, messages.ERROR, 'One or more fields are invalid.')

    return render(request, 'account/signup.html')