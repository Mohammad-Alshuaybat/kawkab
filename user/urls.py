from django.urls import path
from .views import sign_up, log_in, dashboard, edit_tasks, check_new_account_info

urlpatterns = [
    path('check_new_account_info/', check_new_account_info),
    path('sign_up/', sign_up),
    path('log_in/', log_in),
    path('dashboard/', dashboard),
    path('edit_tasks/', edit_tasks),
]
