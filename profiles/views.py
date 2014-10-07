from django.shortcuts import render
from django.contrib.auth.models import User


def profile_view(request, user_id):

    user = User.objects.get(id=user_id)

    return render(request, "profile.html", {
        'profile': user,
        'user': request.user,
    })
    
