from django.urls import path

from app.views import TransactionListView, TransferCreateView

urlpatterns = [
    path("", TransferCreateView.as_view(), name="transfer-create"),
    path("history/", TransactionListView.as_view(), name="transaction-list"),
]
