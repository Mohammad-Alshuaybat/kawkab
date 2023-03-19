from django.urls import path
from .views import sign_up, log_in, dashboard, edit_tasks

urlpatterns = [
    path('sign_up/', sign_up),
    path('log_in/', log_in),
    path('dashboard/', dashboard),
    path('edit_tasks/', edit_tasks),
]
