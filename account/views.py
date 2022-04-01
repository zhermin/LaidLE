from django.shortcuts import render, redirect
from django.db import IntegrityError, connection
from django.contrib import messages

# Create your views here.
def login_view(request):

    # TODO: login to other roles, after member/role tables?
    if request.POST:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name, email, role
                FROM person
                WHERE email <> 'anonymous'
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
            return redirect(f'/{person[2]}')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid email or password.')

    return render(request, 'account/login.html')

def logout_view(request):

    if 'role' in request.session:
        request.session.flush()
    return redirect('/')

def signup_view(request):

    # TODO: if already in person table, error = email already registered, use a different email
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

                messages.add_message(request, messages.SUCCESS, 'Registration successful!')
                return redirect('login')

        except IntegrityError as e:
            messages.add_message(request, messages.ERROR, 'One or more fields are invalid.')

    return render(request, 'account/signup.html')