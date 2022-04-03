from django.shortcuts import render, redirect
from django.db import connection

# Create your views here.
def index_view(request):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.pic, p.name, SUM(dd.donation_amt)
            FROM person p, donor d, donation dd
            WHERE p.email = d.email
            AND dd.donor_email = d.email
            AND p.email <> 'anonymous_donor'
            AND dd.donation_date >= NOW() - INTERVAL '1 MONTH'
            GROUP BY p.pic, p.name
            ORDER BY SUM(dd.donation_amt) DESC LIMIT 3;
        """)
        top_donors_thismth = cursor.fetchall()

        cursor.execute("""
            SELECT p.pic, p.name, SUM(dd.donation_amt)
            FROM person p, donor d, donation dd
            WHERE p.email = d.email
            AND dd.donor_email = d.email
            AND p.email <> 'anonymous_donor'
            GROUP BY p.pic, p.name
            ORDER BY SUM(dd.donation_amt) DESC LIMIT 5;
        """)
        top_donors_alltime = cursor.fetchall()

    context = {
        'top_donors_thismth': top_donors_thismth,
        'top_donors_alltime': top_donors_alltime,
    }

    return render(request, 'index.html', context)

def donation_view(request):

    if request.POST:
        print(request.POST['donation_amt'])
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO donation (donor_email, merchant_email, donation_amt)
                VALUES (%(donor_email)s,
                        CASE
                            WHEN EXISTS (SELECT 1 FROM merchant WHERE email = %(merchant_email)s) THEN %(merchant_email)s
                            ELSE 'anonymous_merchant'
                        END,
                        %(donation_amt)s);
            """, {
                'donor_email': request.session['email'] 
                            if 'role' in request.session
                            and request.session['role'] == 'donor'
                            else 'anonymous_donor',
                'merchant_email': request.GET.get('merchant'), # able to donate from a store using URL from QR code
                'donation_amt': request.POST['donation_amt'],
            })
            return redirect('/')

    return render(request, 'core/donation.html')