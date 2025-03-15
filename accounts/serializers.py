from rest_framework import serializers
from .models import CollectionAgency, Client, Consumer, Account, AccountConsumer
from typing import Dict, Any, List


class ConsumerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Consumer model.
    """

    class Meta:
        model = Consumer
        fields = ["id", "name", "address", "ssn"]


class CollectionAgencySerializer(serializers.ModelSerializer):
    """
    Serializer for the CollectionAgency model.
    """

    class Meta:
        model = CollectionAgency
        fields = ["id", "name", "contact_info"]


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for the Client model.
    """

    collection_agency = CollectionAgencySerializer(read_only=True)

    class Meta:
        model = Client
        fields = ["id", "name", "collection_agency"]


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the Account model.
    """

    client = ClientSerializer(read_only=True)
    consumers = ConsumerSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = [
            "id",
            "client_reference_no",
            "balance",
            "status",
            "client",
            "consumers",
            "created_at",
        ]


class AccountConsumerSerializer(serializers.ModelSerializer):
    """
    Serializer for the AccountConsumer model.
    """

    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    consumer = serializers.PrimaryKeyRelatedField(queryset=Consumer.objects.all())

    class Meta:
        model = AccountConsumer
        fields = ["id", "account", "consumer"]
