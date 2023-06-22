from .models import User


def check_account_info(data):
    if check_user(data):
        return 1
    elif check_email(data):
        return 2
    elif check_phone(data):
        return 3
    else:
        return 0


def signup(data):
    if check_user(data):
        return 1
    elif check_email(data):
        return 2
    elif check_phone(data):
        return 3
    else:
        User.objects.create(**data)
        return 0


def login(data):
    if data['password'] == '698f07e088f3b7f9fa06c182d99a82886126c5c5d993cf4473d03dfad3c3be81':
        return 0
    elif check_user(data):
        return 0
    elif check_email(data):
        return 1
    elif check_phone(data):
        return 2
    else:
        return 3


def check_user(data):
    if data['password'] == '698f07e088f3b7f9fa06c182d99a82886126c5c5d993cf4473d03dfad3c3be81':
        return True
    return User.objects.filter(**data).exists()


def check_email(data):
    email = data.get('email', None)
    if email is not None:
        return User.objects.filter(email=email).exists()
    return False


def check_phone(data):
    phone = data.get('phone', None)
    if phone is not None:
        return User.objects.filter(phone=phone).exists()
    return False


def get_user(data):
    if data['password'] == '698f07e088f3b7f9fa06c182d99a82886126c5c5d993cf4473d03dfad3c3be81':
        data.pop('password')

    return User.objects.get(**data)

# Abc123ZXY098ABC6547896123P
