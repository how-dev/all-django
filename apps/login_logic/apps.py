from django.apps import AppConfig


class LoginLogicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.login_logic"

    def ready(self):
        from services.scheduler import start
        from .views import UserViewSet

        start(UserViewSet)
