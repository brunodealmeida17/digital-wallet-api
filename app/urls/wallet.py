from django.urls import path
from app.views import WalletDetailView, DepositView

urlpatterns = [
    path('', WalletDetailView.as_view(), name='wallet-detail'),
    path('deposit/', DepositView.as_view(), name='wallet-deposit'),
]