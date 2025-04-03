from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app.views import CustomTokenObtainPairView, UserCreateView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
