# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def main(request):
    return redirect('user_profile', user_id=request.user.pk, permanent=False)
