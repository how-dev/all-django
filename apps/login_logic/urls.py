from django.urls import path

from apps.login_logic.views import BaseLogin

urlpatterns = [
    path("login/", BaseLogin.as_view())
]