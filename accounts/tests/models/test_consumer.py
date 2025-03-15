from django.test import TestCase
from accounts.models import Consumer


class ConsumerModelTest(TestCase):
    """Test cases for the Consumer model."""

    def test_create_consumer(self):
        """Test creating a consumer."""
        consumer = Consumer.objects.create(
            name="John Doe", address="123 Main St", ssn="123-45-6789"
        )
        self.assertEqual(consumer.name, "John Doe")
        self.assertEqual(consumer.address, "123 Main St")
        self.assertEqual(consumer.ssn, "123-45-6789")
        self.assertIsNotNone(consumer.created_at)
        self.assertIsNotNone(consumer.updated_at)
