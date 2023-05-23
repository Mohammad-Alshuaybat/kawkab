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
    if check_user(data):
        return 0
    elif check_email(data) or check_phone(data):
        return 1
    else:
        return 2


def check_user(data):
    return User.objects.filter(**data).exists()


def check_email(data):
    return User.objects.filter(email=data.get('email', None)).exists()


def check_phone(data):
    return User.objects.filter(phone=data.get('phone', None)).exists()


def get_user(data):
    return User.objects.get(**data)

