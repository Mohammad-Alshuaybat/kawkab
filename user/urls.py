from django.urls import path
from .views import statistics, sign_up, check_user

urlpatterns = [
    # path('check_new_account_info/', check_new_account_info),
    path('sign_up/', sign_up),
    path('check_user/', check_user),
    # path('log_in/', log_in),
    # path('dashboard/', dashboard),
    # path('edit_tasks/', edit_tasks),
    path('statistics/', statistics),
]
