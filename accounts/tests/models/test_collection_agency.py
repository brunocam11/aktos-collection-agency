from django.test import TestCase
from accounts.models import CollectionAgency, Client


class CollectionAgencyModelTest(TestCase):
    """Test cases for the CollectionAgency model."""

    def test_create_collection_agency(self):
        """Test creating a collection agency."""
        agency = CollectionAgency.objects.create(name="Test Agency")
        self.assertEqual(agency.name, "Test Agency")
        self.assertIsNotNone(agency.created_at)
        self.assertIsNotNone(agency.updated_at)

    def test_get_clients(self):
        """Test getting clients for a collection agency."""
        agency = CollectionAgency.objects.create(name="Test Agency")
        client1 = Client.objects.create(name="Client 1", collection_agency=agency)
        client2 = Client.objects.create(name="Client 2", collection_agency=agency)

        clients = agency.get_clients()
        self.assertEqual(len(clients), 2)
        self.assertIn(client1, clients)
        self.assertIn(client2, clients)
