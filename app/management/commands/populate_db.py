from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import Wallet, Transfer
from decimal import Decimal
import random
from faker import Faker

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Populates the database with fake data'
    
    def handle(self, *args, **options):
        self.stdout.write("Creating users and wallets...")
        
        users = []
        for i in range(10):
            user = User.objects.create_user(
                email=fake.unique.email(),
                username=fake.user_name(),
                cpf=fake.unique.numerify('###########'),
                password='password123'
            )
            wallet, _ = Wallet.objects.get_or_create(user=user)
            wallet.deposit(Decimal(str(random.uniform(100, 1000))).quantize(Decimal('0.01')))
            users.append(user)
            self.stdout.write(f"Created user {user.email} with wallet balance {wallet.balance}")
        
        # Criando transferências
        self.stdout.write("Creating transfers...")
        for i in range(20):
            sender, receiver = random.sample(users, 2)
            amount = Decimal(random.uniform(10, 200)).quantize(Decimal('0.01'))
            
            try:
                Transfer.objects.create(
                    sender=sender.wallet,
                    receiver=receiver.wallet,
                    amount=amount,
                    description=fake.sentence()
                )
                self.stdout.write(f"Transfer {amount} from {sender.email} to {receiver.email}")
            except Exception as e:
                self.stdout.write(f"Failed to create transfer: {str(e)}")
        
        self.stdout.write(self.style.SUCCESS("Successfully populated the database"))
