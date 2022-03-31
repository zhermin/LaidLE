from django.shortcuts import render, redirect
from django.db import IntegrityError, connection

# Create your views here.
def login_view(request):

    # TODO: login to other roles, after member/role tables?
    if request.POST:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT donor_name, donor_email
                FROM donor
                WHERE donor_email <> 'anonymous'
                AND donor_email = %(email)s
                AND donor_pw = crypt(%(password)s, donor_pw);
            """, {
                'email': request.POST['email'],
                'password': request.POST['password'],
            })
            donor = cursor.fetchone()

        if donor:
            request.session['role'] = 'donor' # TODO: member/role table
            request.session['name'] = donor[0]
            request.session['email'] = donor[1]
            return redirect('donor:donor')
        else:
            return render(request, 'account/login.html', {
                'status': 'Incorrect email or password.',
            })

    return render(request, 'account/login.html')

def logout_view(request):

    if 'role' in request.session:
        request.session.flush()
    return redirect('/')
    # return render(request, 'account/logout.html')

def signup_view(request):

    if request.POST:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO donor (donor_name, donor_email, donor_pw)
                    VALUES (%(donor_name)s, %(donor_email)s, crypt(%(donor_pw)s, gen_salt('bf')));
                """, {
                    'donor_name': request.POST['donor_name'],
                    'donor_email': request.POST['donor_email'],
                    'donor_pw': request.POST['donor_pw'],
                })
                return redirect('login')
        except IntegrityError as e:
            print(dir(e))
            return render(request, 'account/signup.html', {
                'status': e.__cause__,
            })

    return render(request, 'account/signup.html')