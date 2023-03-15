from django.urls import path
from .views import sign_up, log_in, dashboard

urlpatterns = [
    path('sign_up/', sign_up),
    path('log_in/', log_in),
    path('dashboard/', dashboard),
]
