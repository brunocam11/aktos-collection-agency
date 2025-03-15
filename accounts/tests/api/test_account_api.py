from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CollectionAgency, Client, Consumer, Account, AccountConsumer
from decimal import Decimal


class AccountsAPITest(TestCase):
    """Test cases for the accounts API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create a collection agency
        self.agency = CollectionAgency.objects.create(name="Test Agency")

        # Create a client
        self.test_client = Client.objects.create(
            name="Test Client", collection_agency=self.agency
        )

        # Create consumers
        self.consumer1 = Consumer.objects.create(
            name="John Doe", address="123 Main St", ssn="123-45-6789"
        )
        self.consumer2 = Consumer.objects.create(
            name="Jane Smith", address="456 Oak Ave", ssn="987-65-4321"
        )

        # Create accounts
        self.account1 = Account.objects.create(
            client_reference_no="REF001",
            balance=Decimal("100.00"),
            status=Account.STATUS_IN_COLLECTION,
            client=self.test_client,
        )
        self.account2 = Account.objects.create(
            client_reference_no="REF002",
            balance=Decimal("500.00"),
            status=Account.STATUS_PAID_IN_FULL,
            client=self.test_client,
        )
        self.account3 = Account.objects.create(
            client_reference_no="REF003",
            balance=Decimal("2000.00"),
            status=Account.STATUS_INACTIVE,
            client=self.test_client,
        )

        # Link accounts and consumers
        AccountConsumer.objects.create(account=self.account1, consumer=self.consumer1)
        AccountConsumer.objects.create(account=self.account2, consumer=self.consumer1)
        AccountConsumer.objects.create(account=self.account3, consumer=self.consumer2)

    def test_get_accounts_no_filters(self):
        """Test getting all accounts without filters."""
        url = reverse("account-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_filter_by_min_balance(self):
        """Test filtering accounts by minimum balance."""
        url = reverse("account-list")
        response = self.client.get(url, {"min_balance": 200})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        for account in response.data["results"]:
            self.assertGreaterEqual(Decimal(account["balance"]), Decimal(200))

    def test_filter_by_max_balance(self):
        """Test filtering accounts by maximum balance."""
        url = reverse("account-list")
        response = self.client.get(url, {"max_balance": 500})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        for account in response.data["results"]:
            self.assertLessEqual(Decimal(account["balance"]), Decimal(500))

    def test_filter_by_min_and_max_balance(self):
        """Test filtering accounts by minimum and maximum balance."""
        url = reverse("account-list")
        response = self.client.get(url, {"min_balance": 100, "max_balance": 500})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        for account in response.data["results"]:
            self.assertGreaterEqual(Decimal(account["balance"]), Decimal(100))
            self.assertLessEqual(Decimal(account["balance"]), Decimal(500))

    def test_filter_by_status(self):
        """Test filtering accounts by status."""
        url = reverse("account-list")
        response = self.client.get(url, {"status": Account.STATUS_IN_COLLECTION})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["status"], Account.STATUS_IN_COLLECTION
        )

    def test_filter_by_consumer_name(self):
        """Test filtering accounts by consumer name."""
        url = reverse("account-list")
        response = self.client.get(url, {"consumer_name": "John"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        # Verify the correct accounts are returned
        client_refs = [
            account["client_reference_no"] for account in response.data["results"]
        ]
        self.assertIn("REF001", client_refs)
        self.assertIn("REF002", client_refs)

    def test_filter_by_combined_criteria(self):
        """Test filtering accounts by multiple criteria."""
        url = reverse("account-list")
        response = self.client.get(
            url,
            {
                "min_balance": 100,
                "max_balance": 1000,
                "status": Account.STATUS_PAID_IN_FULL,
                "consumer_name": "John",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["client_reference_no"], "REF002")

    def test_filter_no_results(self):
        """Test filtering with criteria that should return no results."""
        url = reverse("account-list")
        response = self.client.get(
            url,
            {
                "min_balance": 5000,  # Higher than any account balance
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
