from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, filters, status, parsers
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, parser_classes
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from django_filters import NumberFilter
from decimal import Decimal
from typing import Any, Dict, Optional, List

from .models import CollectionAgency, Client, Consumer, Account, AccountConsumer
from .serializers import (
    CollectionAgencySerializer,
    ClientSerializer,
    ConsumerSerializer,
    AccountSerializer,
    AccountConsumerSerializer,
)
from .services import CSVImportService, CSVImportError
from .pagination import AccountCursorPagination


class AccountFilter(FilterSet):
    """
    Filter set for the Account model with custom filters for min_balance, max_balance,
    consumer_name, and status.
    """

    min_balance = NumberFilter(field_name="balance", lookup_expr="gte")
    max_balance = NumberFilter(field_name="balance", lookup_expr="lte")
    consumer_name = CharFilter(method="filter_consumer_name")
    status = CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = Account
        fields = ["min_balance", "max_balance", "consumer_name", "status"]

    def filter_consumer_name(self, queryset, name, value):
        """
        Custom filter method to filter accounts by consumer name.

        Args:
            queryset: The initial queryset
            name: The name of the filter
            value: The consumer name to filter by

        Returns:
            Filtered queryset of accounts that have consumers with names containing the value
        """
        if not value:
            return queryset
        return queryset.filter(consumers__name__icontains=value).distinct()


class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for accounts with filtering capabilities.
    """

    queryset = (
        Account.objects.all()
        .select_related("client__collection_agency")
        .prefetch_related("consumers")
    )
    serializer_class = AccountSerializer
    filterset_class = AccountFilter
    pagination_class = AccountCursorPagination

    def get_queryset(self):
        """
        Get the queryset for this view.

        Returns:
            Queryset of accounts, optionally filtered by query parameters
        """
        queryset = super().get_queryset()

        # If there are no filters, return all accounts
        if not self.request.query_params:
            return queryset

        # Create filter instance
        filter_instance = self.filterset_class(
            self.request.query_params, queryset=queryset
        )

        # Return filtered queryset
        return filter_instance.qs

    @action(
        detail=False,
        methods=["POST"],
        url_path="upload-csv",
        parser_classes=[parsers.MultiPartParser, parsers.FormParser],
    )
    def upload_csv(self, request):
        """
        Upload a CSV file to import account data.

        Request Parameters:
            file: The CSV file to upload
            collection_agency_id: ID of the collection agency
            client_id: ID of the client

        Returns:
            Dictionary with import statistics or error message
        """
        # Validate required parameters
        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        if "collection_agency_id" not in request.data:
            return Response(
                {"error": "collection_agency_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "client_id" not in request.data:
            return Response(
                {"error": "client_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get parameters
            csv_file = request.FILES["file"]
            collection_agency_id = int(request.data["collection_agency_id"])
            client_id = int(request.data["client_id"])

            # Process CSV file
            result = CSVImportService.process_csv_file(
                csv_file, collection_agency_id, client_id
            )

            return Response(result, status=status.HTTP_200_OK)

        except CSVImportError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConsumerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for consumers.
    """

    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer
    pagination_class = AccountCursorPagination


class ClientViewSet(viewsets.ModelViewSet):
    """
    API endpoint for clients.
    """

    queryset = Client.objects.all().select_related("collection_agency")
    serializer_class = ClientSerializer
    pagination_class = AccountCursorPagination


class CollectionAgencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for collection agencies.
    """

    queryset = CollectionAgency.objects.all()
    serializer_class = CollectionAgencySerializer
    pagination_class = AccountCursorPagination
