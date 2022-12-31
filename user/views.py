from django.db import IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User


@api_view(['POST'])
def sign_up(request):
    # 0-->account_created  1-->account_already_exit  2-->email_is_used  3-->phone_num_is_used  4-->sth_goes_wrong
    data = request.data
    try:
        user, created = User.objects.get_or_create(**data)

        if created:
            return Response(0)
        else:
            return Response(1)

    except IntegrityError as e:
        print(e)
        if e.args[0] == 'UNIQUE constraint failed: user_user.email':
            return Response(2)
        elif e.args[0] == 'UNIQUE constraint failed: user_user.phone':
            return Response(3)

    return Response(4)
# {
#     "email": "malek315@gmail.com",
#     "phone": "0786636678",
#     "password": "password",
#     "firstName": "malek",
#     "lastName": "aldebsi",
#     "section": "s",
#     "grade": 8
# }


@api_view(['POST'])
def log_in(request):
    # 0-->logged_in  1-->email_or_password_are_wrong
    data = request.data

    try:
        user = User.objects.get(**data)
        return Response(0)
    except:
        return Response(1)
# {
#     "email": "malek315@gmail.com",
#     "password": "password"
# }
# or
# {
#     "phone": "0786636678",
#     "password": "password"
# }


@api_view(['POST'])
def user_name(request):
    # username  0-->sth_goes_wrong
    data = request.data

    try:
        user = User.objects.get(**data)
        return Response(user.firstName)
    except:
        return Response(0)
# {
#     "email": "malek315@gmail.com",
#     "password": "password"
# }
# or
# {
#     "phone": "0786636678",
#     "password": "password"
# }
