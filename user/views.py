from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.utils import signup, login, check_user, get_user


@api_view(['POST'])
def sign_up(request):
    # 0-->account_created  1-->account_already_exit  2-->email_is_used  3-->phone_num_is_used
    data = request.data
    return Response(signup(data))
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
    # 0-->logged_in  1-->password_are_wrong  2-->email_or_phone_not_exist
    data = request.data
    return Response(login(data))
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
    if check_user(data):
        user = get_user(data)
        return Response(user.firstName)
    else:
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
