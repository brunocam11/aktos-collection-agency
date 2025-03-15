from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import CollectionAgency, Client, Consumer, Account, AccountConsumer
from accounts.services import CSVImportService, CSVImportError
import io
from decimal import Decimal


class CSVImportServiceTest(TestCase):
    """Test cases for the CSV import service."""

    def setUp(self):
        """Set up test data."""
        # Create a collection agency and client
        self.agency = CollectionAgency.objects.create(name="Test Agency")
        self.client = Client.objects.create(
            name="Test Client", collection_agency=self.agency
        )

    def test_import_valid_csv(self):
        """Test importing a valid CSV file."""
        # Create a sample CSV content
        csv_content = """client reference no,balance,status,consumer name,consumer address,ssn
REF001,100.50,IN_COLLECTION,John Doe,123 Main St,123-45-6789
REF002,200.75,PAID_IN_FULL,Jane Smith,456 Oak Ave,987-65-4321
REF001,100.50,IN_COLLECTION,Bob Johnson,789 Pine St,555-55-5555"""

        # Convert the string to a file-like object
        csv_file = io.StringIO(csv_content)

        # Process the CSV
        result = CSVImportService.process_csv_file(
            csv_file, collection_agency_id=self.agency.id, client_id=self.client.id
        )

        # Check the results
        self.assertEqual(result["accounts_processed"], 2)  # 2 unique account references
        self.assertEqual(result["accounts_created"], 2)
        self.assertEqual(result["accounts_updated"], 0)
        self.assertEqual(result["consumers_created"], 3)
        self.assertEqual(result["consumer_accounts_linked"], 3)

        # Check the database
        self.assertEqual(Account.objects.count(), 2)
        self.assertEqual(Consumer.objects.count(), 3)
        self.assertEqual(AccountConsumer.objects.count(), 3)

        # Check specific account data
        account1 = Account.objects.get(client_reference_no="REF001")
        self.assertEqual(account1.balance, Decimal("100.50"))
        self.assertEqual(account1.status, Account.STATUS_IN_COLLECTION)
        self.assertEqual(account1.client, self.client)

        # Check account-consumer relationships
        self.assertEqual(account1.consumers.count(), 2)  # Two consumers for REF001

        account2 = Account.objects.get(client_reference_no="REF002")
        self.assertEqual(account2.consumers.count(), 1)  # One consumer for REF002

    def test_import_invalid_csv_headers(self):
        """Test importing a CSV with invalid headers."""
        # CSV with missing 'status' column
        csv_content = """client reference no,balance,consumer name,consumer address,ssn
REF001,100.50,John Doe,123 Main St,123-45-6789
"""

        # Convert the string to a file-like object
        csv_file = io.StringIO(csv_content)

        # Attempt to process the CSV
        with self.assertRaises(CSVImportError) as context:
            CSVImportService.process_csv_file(
                csv_file, collection_agency_id=self.agency.id, client_id=self.client.id
            )

        self.assertIn("Missing required CSV headers", str(context.exception))

    def test_import_invalid_row_data(self):
        """Test importing a CSV with invalid row data."""
        # CSV with invalid balance
        csv_content = """client reference no,balance,status,consumer name,consumer address,ssn
REF001,invalid,IN_COLLECTION,John Doe,123 Main St,123-45-6789
"""

        # Convert the string to a file-like object
        csv_file = io.StringIO(csv_content)

        # Attempt to process the CSV
        with self.assertRaises(CSVImportError) as context:
            CSVImportService.process_csv_file(
                csv_file, collection_agency_id=self.agency.id, client_id=self.client.id
            )

        self.assertIn("Invalid balance", str(context.exception))

    def test_update_existing_account(self):
        """Test updating an existing account."""
        # Create an existing account
        Account.objects.create(
            client_reference_no="REF001",
            balance=Decimal("100.00"),
            status=Account.STATUS_IN_COLLECTION,
            client=self.client,
        )

        # CSV with updated data for REF001
        csv_content = """client reference no,balance,status,consumer name,consumer address,ssn
REF001,150.75,PAID_IN_FULL,John Doe,123 Main St,123-45-6789
"""

        # Convert the string to a file-like object
        csv_file = io.StringIO(csv_content)

        # Process the CSV
        result = CSVImportService.process_csv_file(
            csv_file, collection_agency_id=self.agency.id, client_id=self.client.id
        )

        # Check the results
        self.assertEqual(result["accounts_processed"], 1)
        self.assertEqual(result["accounts_created"], 0)
        self.assertEqual(result["accounts_updated"], 1)

        # Check the updated account
        updated_account = Account.objects.get(client_reference_no="REF001")
        self.assertEqual(updated_account.balance, Decimal("150.75"))
        self.assertEqual(updated_account.status, Account.STATUS_PAID_IN_FULL)
