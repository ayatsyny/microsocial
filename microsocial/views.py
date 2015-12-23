# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def main(requests):
    return redirect('user_profile', user_id=requests.user.pk, permanent=False)
