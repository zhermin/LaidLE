from django.shortcuts import render, redirect
from django.db import connection

# Create your views here.
def donor_view(request):
    if 'role' not in request.session or request.session['role'] != 'donor':
        return redirect('login')
    return render(request, 'donor/index.html')

def donor_donation_view(request):
    if request.POST:
        print(request.POST['donation_amt'])
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO donation (donor_email, merchant_email, donation_amt)
                VALUES (%(donor_email)s, 'chinese@senate.gov', %(donation_amt)s);
            """, {
                'donor_email': request.POST['donor_email'],
                # 'merchant_email': request.POST['merchant_email'],
                'donation_amt': request.POST['donation_amt'],
            })
            return redirect('donor')

    return render(request, './donor/donor_donation.html')