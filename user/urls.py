from django.urls import path
from .views import sign_up, log_in, user_name

urlpatterns = [
    path('sign_up/', sign_up),
    path('log_in/', log_in),
    path('user_name/', user_name),
]
