from django.test import TestCase
from django.db import IntegrityError, transaction
from accounts.models import CollectionAgency, Client, Consumer, Account, AccountConsumer
from decimal import Decimal


class AccountModelTest(TestCase):
    """Test cases for the Account model."""

    def setUp(self):
        self.agency = CollectionAgency.objects.create(name="Test Agency")
        self.client = Client.objects.create(
            name="Test Client", collection_agency=self.agency
        )

    def test_create_account(self):
        """Test creating an account."""
        account = Account.objects.create(
            client_reference_no="REF001",
            balance=Decimal("100.00"),
            status=Account.STATUS_IN_COLLECTION,
            client=self.client,
        )
        self.assertEqual(account.client_reference_no, "REF001")
        self.assertEqual(account.balance, Decimal("100.00"))
        self.assertEqual(account.status, Account.STATUS_IN_COLLECTION)
        self.assertEqual(account.client, self.client)
        self.assertIsNotNone(account.created_at)
        self.assertIsNotNone(account.updated_at)

    def test_unique_client_reference_no(self):
        """Test that client_reference_no must be unique."""
        Account.objects.create(
            client_reference_no="REF001",
            balance=Decimal("100.00"),
            status=Account.STATUS_IN_COLLECTION,
            client=self.client,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Account.objects.create(
                    client_reference_no="REF001",  # Same reference number
                    balance=Decimal("200.00"),
                    status=Account.STATUS_PAID_IN_FULL,
                    client=self.client,
                )

    def test_get_consumers(self):
        """Test getting consumers for an account."""
        account = Account.objects.create(
            client_reference_no="REF001",
            balance=Decimal("100.00"),
            status=Account.STATUS_IN_COLLECTION,
            client=self.client,
        )
        consumer1 = Consumer.objects.create(
            name="John Doe", address="123 Main St", ssn="123-45-6789"
        )
        consumer2 = Consumer.objects.create(
            name="Jane Smith", address="456 Oak Ave", ssn="987-65-4321"
        )
        AccountConsumer.objects.create(account=account, consumer=consumer1)
        AccountConsumer.objects.create(account=account, consumer=consumer2)

        consumers = account.get_consumers()
        self.assertEqual(len(consumers), 2)
        self.assertIn(consumer1, consumers)
        self.assertIn(consumer2, consumers)
