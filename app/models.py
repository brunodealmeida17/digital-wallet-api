from decimal import ROUND_DOWN, Decimal
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator
from django.db import models, transaction


class User(AbstractUser):
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",  # Nome único para evitar conflito
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",  # Nome único para evitar conflito
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "cpf"]

    def __str__(self):
        return self.email


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(0)]  # type: ignore
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Wallet"

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance = Decimal(self.balance) + amount
        self.save()
        Transaction.objects.create(
            wallet=self,
            amount=Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_DOWN),
            transaction_type="DEPOSIT",
            description=f"Deposit of {amount}",
        )

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        self.balance -= Decimal(amount)
        self.save()
        Transaction.objects.create(
            wallet=self,
            amount=Decimal(str(amount)),
            transaction_type="WITHDRAWAL",
            description=f"Withdrawal of {amount}",
        )

    def get_balance(self):
        return self.balance


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAWAL", "Withdrawal"),
        ("TRANSFER", "Transfer"),
    ]

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for {self.wallet.user.email}"


class Transfer(models.Model):
    sender = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="sent_transfers"
    )
    receiver = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="received_transfers"
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transfer of {self.amount} from {self.sender.user.email} to {self.receiver.user.email}"

    def save(self, *args, **kwargs):
        if self.sender == self.receiver:
            raise ValueError("Cannot transfer to yourself")
        if self.amount <= 0:
            raise ValueError("Transfer amount must be positive")
        if self.sender.balance < self.amount:
            raise ValueError("Insufficient funds")

        with transaction.atomic():
            self.sender.withdraw(self.amount)
            self.receiver.deposit(self.amount)
            super().save(*args, **kwargs)

            Transaction.objects.create(
                wallet=self.sender,
                amount=-self.amount,
                transaction_type="TRANSFER",
                description=f"Transfer to {self.receiver.user.email}: {self.description or 'No description'}",
            )

            Transaction.objects.create(
                wallet=self.receiver,
                amount=self.amount,
                transaction_type="TRANSFER",
                description=f"Transfer from {self.sender.user.email}: {self.description or 'No description'}",
            )
