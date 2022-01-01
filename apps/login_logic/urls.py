from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.login_logic.views import BaseLogin, UserViewSet

router = DefaultRouter()
router.register(r"user", UserViewSet)

urlpatterns = router.urls

urlpatterns += [
    path("login/", BaseLogin.as_view()),
    path("export/<str:file_type>/", UserViewSet.as_view({"get": "export_file"}))
]
