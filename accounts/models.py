from django.db import models
from django.core.validators import MinValueValidator
from typing import List, Optional, Dict, Any


class CollectionAgency(models.Model):
    """
    Represents a collection agency that collects debts on behalf of clients.
    
    A collection agency manages debt collection on behalf of clients.
    
    TODO: Add fields for agency contact information and address
    TODO: Consider adding reporting capabilities for agency performance
    """

    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Collection Agencies"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return self.name

    def get_clients(self) -> List["Client"]:
        """
        Return all clients associated with this collection agency.
        """
        return self.clients.all()


class Client(models.Model):
    """
    Represents an organization that hires a collection agency to collect debt on their behalf.
    
    Clients are organizations that hire collection agencies to collect debt on their behalf.
    
    TODO: Add fields for client contact information and specific requirements
    NOTE: Each client is associated with exactly one collection agency in this model
    """

    name = models.CharField(max_length=255)
    collection_agency = models.ForeignKey(
        CollectionAgency, on_delete=models.CASCADE, related_name="clients"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["collection_agency"]),
        ]

    def __str__(self) -> str:
        return self.name

    def get_accounts(self) -> List["Account"]:
        """
        Return all accounts associated with this client.
        """
        return self.accounts.all()


class Consumer(models.Model):
    """
    Represents a person/entity that owes a debt.
    
    Consumers can have multiple accounts (debts) across different clients.
    
    TODO: Implement proper encryption for PII (Personally Identifiable Information)
    TODO: Add more fields for contact details (email, phone)
    NOTE: SSN is stored as plain text currently but should be encrypted in production
    """

    name = models.CharField(max_length=255)
    address = models.TextField()
    ssn = models.CharField(max_length=11)  # Format: XXX-XX-XXXX
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["ssn"]),
        ]

    def __str__(self) -> str:
        return self.name

    def get_accounts(self) -> List["Account"]:
        """
        Return all accounts associated with this consumer.
        """
        return self.accounts.all()


class Account(models.Model):
    """
    Represents a debt account that needs to be collected.
    
    An account is associated with a client and can have multiple consumers.
    
    TODO: Add fields for payment history and collection attempts
    TODO: Implement status transitions with proper validations
    NOTE: The many-to-many relationship with consumers is implemented via AccountConsumer
    """

    # Status choices
    STATUS_IN_COLLECTION = "IN_COLLECTION"
    STATUS_PAID_IN_FULL = "PAID_IN_FULL"
    STATUS_INACTIVE = "INACTIVE"

    STATUS_CHOICES = [
        (STATUS_IN_COLLECTION, "In Collection"),
        (STATUS_PAID_IN_FULL, "Paid in Full"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    client_reference_no = models.CharField(max_length=255, unique=True)
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_COLLECTION
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="accounts"
    )
    consumers = models.ManyToManyField(
        Consumer, through="AccountConsumer", related_name="accounts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["client_reference_no"]),
            models.Index(fields=["balance"]),
            models.Index(fields=["status"]),
            models.Index(fields=["client"]),
        ]

    def __str__(self) -> str:
        return f"Account {self.client_reference_no} - ${self.balance}"

    def get_consumers(self) -> List[Consumer]:
        """
        Return all consumers associated with this account.
        """
        return self.consumers.all()


class AccountConsumer(models.Model):
    """
    Represents the many-to-many relationship between accounts and consumers.
    """

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["account", "consumer"]
        indexes = [
            models.Index(fields=["account"]),
            models.Index(fields=["consumer"]),
        ]

    def __str__(self) -> str:
        return f"{self.consumer} on {self.account}"
