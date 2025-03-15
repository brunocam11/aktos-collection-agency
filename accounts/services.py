import csv
import io
from typing import Dict, List, Any, Optional, Set, Tuple
from django.db import transaction
from django.db.models import Model
from decimal import Decimal, InvalidOperation

from .models import CollectionAgency, Client, Consumer, Account, AccountConsumer


class CSVImportError(Exception):
    """
    Exception raised when there is an error importing CSV data.
    """

    pass


class CSVImportService:
    """
    Service for importing CSV data into the database.
    """

    def __init__(self, collection_agency_id: int, client_id: int):
        """
        Initialize the CSV import service.

        Args:
            collection_agency_id: ID of the collection agency
            client_id: ID of the client
        """
        self.collection_agency_id = collection_agency_id
        self.client_id = client_id

        # Validate collection agency and client
        try:
            self.collection_agency = CollectionAgency.objects.get(
                id=collection_agency_id
            )
            self.client = Client.objects.get(
                id=client_id, collection_agency_id=collection_agency_id
            )
        except CollectionAgency.DoesNotExist:
            raise CSVImportError(
                f"Collection agency with ID {collection_agency_id} does not exist."
            )
        except Client.DoesNotExist:
            raise CSVImportError(
                f"Client with ID {client_id} does not exist or does not belong to the specified collection agency."
            )

    def validate_csv_headers(self, headers: List[str]) -> None:
        """
        Validate that the CSV file has the expected headers.

        Args:
            headers: List of CSV headers

        Raises:
            CSVImportError: If headers do not match expected headers
        """
        expected_headers = [
            "client reference no",
            "balance",
            "status",
            "consumer name",
            "consumer address",
            "ssn",
        ]

        # Check if all expected headers are present
        missing_headers = set(expected_headers) - set(headers)
        if missing_headers:
            raise CSVImportError(
                f"Missing required CSV headers: {', '.join(missing_headers)}"
            )

    def validate_row_data(self, row_data: Dict[str, str], row_num: int) -> None:
        """
        Validate a single row of data from the CSV file.

        Args:
            row_data: Dictionary containing row data
            row_num: Row number for error reporting

        Raises:
            CSVImportError: If row data is invalid
        """
        # Check if required fields are present and non-empty
        required_fields = [
            "client reference no",
            "balance",
            "status",
            "consumer name",
            "consumer address",
            "ssn",
        ]
        for field in required_fields:
            if field not in row_data or not row_data[field]:
                raise CSVImportError(f"Row {row_num}: Missing required field '{field}'")

        # Validate status
        valid_statuses = [
            Account.STATUS_IN_COLLECTION,
            Account.STATUS_PAID_IN_FULL,
            Account.STATUS_INACTIVE,
        ]
        if row_data["status"] not in valid_statuses:
            raise CSVImportError(
                f"Row {row_num}: Invalid status '{row_data['status']}'. Must be one of: {', '.join(valid_statuses)}"
            )

        # Validate balance
        try:
            balance = Decimal(row_data["balance"])
            if balance < 0:
                raise CSVImportError(f"Row {row_num}: Balance must be non-negative")
        except (ValueError, InvalidOperation):
            raise CSVImportError(
                f"Row {row_num}: Invalid balance '{row_data['balance']}'. Must be a number."
            )

    @transaction.atomic
    def import_csv(self, csv_file_obj: Any) -> Dict[str, Any]:
        """
        Import data from a CSV file into the database.

        Args:
            csv_file_obj: CSV file object to read from

        Returns:
            Dictionary with import statistics

        Raises:
            CSVImportError: If there is an error importing the CSV data
        """
        try:
            # Try to determine if we have a file-like object or raw text
            if hasattr(csv_file_obj, "read"):
                # If file-like object, read content
                csv_content = csv_file_obj.read()
                if isinstance(csv_content, bytes):
                    csv_content = csv_content.decode("utf-8")
            else:
                # Assuming it's already a string
                csv_content = csv_file_obj

            # Create CSV reader from string content
            csv_reader = csv.DictReader(io.StringIO(csv_content))

            # Validate CSV headers
            self.validate_csv_headers(csv_reader.fieldnames)

            # Statistics counters
            account_refs_processed = set()
            accounts_created = 0
            accounts_updated = 0
            consumers_created = 0
            consumer_accounts_linked = 0

            # Track account references to create or update
            account_data = {}
            consumer_data = {}
            account_consumer_links = []

            # Process each row in the CSV
            for row_num, row in enumerate(
                csv_reader, start=2
            ):  # Start from 2 to account for headers
                # Validate row data
                self.validate_row_data(row, row_num)

                # Process account data (we may see the same account reference multiple times)
                client_ref = row["client reference no"]
                account_refs_processed.add(client_ref)

                # Track account data (use the first occurrence for account data)
                if client_ref not in account_data:
                    account_data[client_ref] = {
                        "balance": Decimal(row["balance"]),
                        "status": row["status"],
                        "client_id": self.client.id,
                    }

                # Process consumer data
                consumer_key = (
                    row["consumer name"],
                    row["consumer address"],
                    row["ssn"],
                )
                if consumer_key not in consumer_data:
                    consumer_data[consumer_key] = {
                        "name": row["consumer name"],
                        "address": row["consumer address"],
                        "ssn": row["ssn"],
                    }

                # Track account-consumer link
                account_consumer_links.append((client_ref, consumer_key))

            # Process accounts (create or update)
            for client_ref, data in account_data.items():
                account, created = Account.objects.update_or_create(
                    client_reference_no=client_ref,
                    defaults={
                        "balance": data["balance"],
                        "status": data["status"],
                        "client_id": data["client_id"],
                    },
                )
                if created:
                    accounts_created += 1
                else:
                    accounts_updated += 1

            # Process consumers (create only if they don't exist)
            for consumer_key, data in consumer_data.items():
                consumer, created = Consumer.objects.get_or_create(
                    ssn=data["ssn"],
                    defaults={"name": data["name"], "address": data["address"]},
                )
                if created:
                    consumers_created += 1

            # Link accounts and consumers
            for client_ref, consumer_key in account_consumer_links:
                account = Account.objects.get(client_reference_no=client_ref)
                consumer = Consumer.objects.get(ssn=consumer_data[consumer_key]["ssn"])

                # Create the link if it doesn't exist
                link, created = AccountConsumer.objects.get_or_create(
                    account=account, consumer=consumer
                )
                if created:
                    consumer_accounts_linked += 1

            # Return statistics
            return {
                "accounts_processed": len(account_refs_processed),
                "accounts_created": accounts_created,
                "accounts_updated": accounts_updated,
                "consumers_created": consumers_created,
                "consumer_accounts_linked": consumer_accounts_linked,
            }

        except Exception as e:
            # Rollback the transaction on any error
            transaction.set_rollback(True)
            if isinstance(e, CSVImportError):
                raise
            raise CSVImportError(f"Error importing CSV: {str(e)}")

    @classmethod
    def process_csv_file(
        cls, file_obj: Any, collection_agency_id: int, client_id: int
    ) -> Dict[str, Any]:
        """
        Process a CSV file and import its data.

        Args:
            file_obj: CSV file object
            collection_agency_id: ID of the collection agency
            client_id: ID of the client

        Returns:
            Dictionary with import statistics
        """
        service = cls(collection_agency_id, client_id)
        return service.import_csv(file_obj)
