from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Transaction, Transfer, Wallet

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "cpf", "password"]
        extra_kwargs = {"password": {"write_only": True}, "cpf": {"required": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            cpf=validated_data["cpf"],
            password=validated_data["password"],
        )
        Wallet.objects.create(user=user)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token


class WalletSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Wallet
        fields = ["id", "user_email", "balance", "created_at", "updated_at"]
        read_only_fields = ["id", "user_email", "created_at", "updated_at"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "amount", "transaction_type", "description", "created_at"]
        read_only_fields = fields


class TransferSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source="sender.user.email", read_only=True)
    receiver_email = serializers.EmailField(
        source="receiver.user.email", read_only=True
    )

    class Meta:
        model = Transfer
        fields = [
            "id",
            "sender",
            "sender_email",
            "receiver",
            "receiver_email",
            "amount",
            "description",
            "created_at",
        ]
        extra_kwargs = {
            "sender": {"write_only": True},
            "receiver": {"write_only": True},
        }

    def validate(self, data):
        if data["sender"] == data["receiver"]:
            raise serializers.ValidationError("Cannot transfer to yourself")
        if data["amount"] <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return data


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
