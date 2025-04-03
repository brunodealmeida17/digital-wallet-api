from django.urls import path

from app.views import DepositView, WalletDetailView

urlpatterns = [
    path("", WalletDetailView.as_view(), name="wallet-detail"),
    path("deposit/", DepositView.as_view(), name="wallet-deposit"),
]
