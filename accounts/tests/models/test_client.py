from django.test import TestCase
from accounts.models import CollectionAgency, Client, Account
from decimal import Decimal


class ClientModelTest(TestCase):
    """Test cases for the Client model."""

    def setUp(self):
        self.agency = CollectionAgency.objects.create(name="Test Agency")

    def test_create_client(self):
        """Test creating a client."""
        client = Client.objects.create(
            name="Test Client", collection_agency=self.agency
        )
        self.assertEqual(client.name, "Test Client")
        self.assertEqual(client.collection_agency, self.agency)
        self.assertIsNotNone(client.created_at)
        self.assertIsNotNone(client.updated_at)

    def test_get_accounts(self):
        """Test getting accounts for a client."""
        client = Client.objects.create(
            name="Test Client", collection_agency=self.agency
        )
        account1 = Account.objects.create(
            client_reference_no="REF001",
            balance=Decimal("100.00"),
            status=Account.STATUS_IN_COLLECTION,
            client=client,
        )
        account2 = Account.objects.create(
            client_reference_no="REF002",
            balance=Decimal("200.00"),
            status=Account.STATUS_PAID_IN_FULL,
            client=client,
        )

        accounts = client.get_accounts()
        self.assertEqual(len(accounts), 2)
        self.assertIn(account1, accounts)
        self.assertIn(account2, accounts)
