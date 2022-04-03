from django.shortcuts import render, redirect
from django.db import IntegrityError, connection
from django.contrib import messages
from account.decorators import check_permissions

# Create your views here.
@check_permissions('donor')
def donor_view(request):

    if request.POST:
        if request.POST['action'] == 'redeem':
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO redemption (reward_sn, donor_email)
                    VALUES (%(reward_sn)s, %(donor_email)s);
                """, {
                    'reward_sn': request.POST['reward_sn'],
                    'donor_email': request.session['email'],
                })
                messages.add_message(request, messages.SUCCESS, 'Reward redeemed successfully!')
                return redirect(f'reward/{request.POST["reward_sn"]}')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT coin FROM donor
            WHERE donor.email = %(email)s;
        """, {
            'email': request.session['email'],
        })
        coins = cursor.fetchone()[0]

        cursor.execute("""
            SELECT r.reward_sn, r.reward_name, r.reward_desc, r.reward_price, r.reward_qty
            FROM reward r
            ORDER BY r.reward_price;
        """)
        rewards = cursor.fetchall()

    context = {
        "coins": coins,
        "rewards": rewards
    }

    return render(request, 'donor/index.html', context)

@check_permissions('donor')
def profile_view(request):
    return render(request, 'account/profile.html')

@check_permissions('donor')
def generated_reward_view(request, reward_sn):

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT r.reward_sn, rd.redeem_date, r.reward_name, r.reward_desc
                FROM reward r, redemption rd
                WHERE r.reward_sn = %(reward_sn)s
                AND r.reward_sn = rd.reward_sn;
            """, {
                'reward_sn': reward_sn,
            })
            reward = cursor.fetchone()
    except IntegrityError:
        messages.add_message(request, messages.ERROR, 'Error claiming reward! Check if you have sufficient coins.')

    context = {
        "reward": reward
    }

    return render(request, 'donor/reward.html', context)