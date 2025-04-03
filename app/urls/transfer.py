from django.urls import path
from app.views import TransferCreateView, TransactionListView

urlpatterns = [
    path('', TransferCreateView.as_view(), name='transfer-create'),
    path('history/', TransactionListView.as_view(), name='transaction-list'),
]