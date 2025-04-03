from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from app.models import Wallet, Transfer
from decimal import Decimal

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'cpf': '12345678901',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('1000.00'))
    
    def test_user_registration(self):
        url = reverse('register')
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'cpf': '98765432109',
            'password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
    
    def test_user_login(self):
        url = reverse('login')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class WalletTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='wallet@test.com',
            username='wallettest',
            cpf='11122233344',
            password='testpass123'
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('500.00'))
        
        # Authenticate
        response = self.client.post(
            reverse('login'),
            {'email': 'wallet@test.com', 'password': 'testpass123'},
            format='json'
        )
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_get_wallet_balance(self):
        url = reverse('wallet-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['balance']), self.wallet.balance)
    
    def test_deposit_to_wallet(self):
        url = reverse('wallet-deposit')
        data = {'amount': '200.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('700.00'))
    
    def test_invalid_deposit(self):
        url = reverse('wallet-deposit')
        data = {'amount': '-50.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TransferTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create sender user
        self.sender = User.objects.create_user(
            email='sender@test.com',
            username='sendertest',
            cpf='55566677788',
            password='testpass123'
        )
        self.sender_wallet = Wallet.objects.create(user=self.sender, balance=Decimal('1000.00'))
        
        # Create receiver user
        self.receiver = User.objects.create_user(
            email='receiver@test.com',
            username='receivertest',
            cpf='99988877766',
            password='testpass123'
        )
        self.receiver_wallet = Wallet.objects.create(user=self.receiver, balance=Decimal('500.00'))
        
        # Authenticate as sender
        response = self.client.post(
            reverse('login'),
            {'email': 'sender@test.com', 'password': 'testpass123'},
            format='json'
        )
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_transfer(self):
        url = reverse('transfer-create')
        data = {
            'sender': self.sender_wallet.id,
            'receiver': self.receiver_wallet.id,
            'amount': '200.00',
            'description': 'Test transfer'
        }
        response = self.client.post(url, data, format='json')
        print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.sender_wallet.refresh_from_db()
        self.receiver_wallet.refresh_from_db()
        
        self.assertEqual(self.sender_wallet.balance, Decimal('800.00'))
        self.assertEqual(self.receiver_wallet.balance, Decimal('700.00'))
    
    def test_insufficient_funds_transfer(self):
        url = reverse('transfer-create')
        data = {
            'receiver': self.receiver_wallet.id,
            'amount': '2000.00',
            'description': 'Test transfer with insufficient funds'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_transfer_to_self(self):
        url = reverse('transfer-create')
        data = {
            'receiver': self.sender_wallet.id,
            'amount': '100.00',
            'description': 'Test transfer to self'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TransactionHistoryTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='history@test.com',
            username='historytest',
            cpf='12312312312',
            password='testpass123'
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('1000.00'))
        
        # Create some transactions
        self.wallet.deposit(Decimal('200.00'))
        self.wallet.withdraw(Decimal('100.00'))
        
        # Authenticate
        response = self.client.post(
            reverse('login'),
            {'email': 'history@test.com', 'password': 'testpass123'},
            format='json'
        )
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_get_transaction_history(self):
        url = reverse('transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Deposit and withdrawal
    
    def test_filter_transactions_by_date(self):
        url = reverse('transaction-list')
        
        # Get today's date in YYYY-MM-DD format
        today = self.wallet.transactions.first().created_at.strftime('%Y-%m-%d')
        
        response = self.client.get(url, {'start_date': today})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)