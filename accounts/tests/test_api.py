from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from accounts.models import Account, Client, Consumer, CollectionAgency
from accounts.serializers import AccountSerializer
from decimal import Decimal


class AccountsAPITest(APITestCase):
    """
    Test cases for the accounts API endpoints.
    """

    def setUp(self):
        """Set up test data."""
        # Create test data
        self.collection_agency = CollectionAgency.objects.create(name="Test Agency")
        self.client_obj = Client.objects.create(
            name="Test Client", collection_agency=self.collection_agency
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
            client=self.client_obj,
            client_reference_no="REF001",
            balance=Decimal("100.50"),
            status="IN_COLLECTION",
        )
        self.account2 = Account.objects.create(
            client=self.client_obj,
            client_reference_no="REF002",
            balance=Decimal("200.75"),
            status="PAID_IN_FULL",
        )
        self.account3 = Account.objects.create(
            client=self.client_obj,
            client_reference_no="REF003",
            balance=Decimal("1500.00"),
            status="IN_COLLECTION",
        )

        # Connect accounts to consumers
        self.account1.consumers.add(self.consumer1)
        self.account2.consumers.add(self.consumer2)
        self.account3.consumers.add(self.consumer1, self.consumer2)

        # Setup API client
        self.client = APIClient()
        self.accounts_url = reverse("account-list")
        self.upload_csv_url = reverse("account-upload-csv")

    # ... existing test methods ...

    @patch("accounts.services.CSVImportService.process_csv_file")
    def test_upload_csv(self, mock_process):
        """Test the CSV upload endpoint."""
        # Set up the mock service to return a successful result
        mock_process.return_value = {"accounts_created": 2, "consumers_created": 2}

        # Create a simple CSV file
        csv_content = b"client reference no,balance,status,consumer name,consumer address,ssn\nREF004,300.25,IN_COLLECTION,Test User,789 Pine St,456-78-9012"
        csv_file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")

        # Prepare data for the request
        data = {
            "file": csv_file,
            "collection_agency_id": self.collection_agency.id,
            "client_id": self.client_obj.id,
        }

        # Make the request
        response = self.client.post(self.upload_csv_url, data, format="multipart")

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the service was called with correct arguments
        mock_process.assert_called_once()
        args, kwargs = mock_process.call_args
        self.assertEqual(kwargs, {})

        # Verify the file and IDs were passed correctly
        # First argument should be the file
        self.assertEqual(args[1], self.collection_agency.id)
        self.assertEqual(args[2], self.client_obj.id)

    @patch("accounts.services.CSVImportService.process_csv_file")
    def test_upload_csv_missing_parameters(self, mock_process):
        """Test the CSV upload endpoint with missing parameters."""
        # Create a simple CSV file
        csv_content = b"client reference no,balance,status,consumer name,consumer address,ssn\nREF004,300.25,IN_COLLECTION,Test User,789 Pine St,456-78-9012"
        csv_file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")

        # Test missing file
        data = {
            "collection_agency_id": self.collection_agency.id,
            "client_id": self.client_obj.id,
        }
        response = self.client.post(self.upload_csv_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("No file provided", response.data["error"])

        # Test missing collection_agency_id
        data = {"file": csv_file, "client_id": self.client_obj.id}
        response = self.client.post(self.upload_csv_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("collection_agency_id is required", response.data["error"])

        # Test missing client_id
        data = {"file": csv_file, "collection_agency_id": self.collection_agency.id}
        response = self.client.post(self.upload_csv_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("client_id is required", response.data["error"])

        # Verify the service was never called
        mock_process.assert_not_called()
