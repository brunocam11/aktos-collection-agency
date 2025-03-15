from django.contrib import admin
from .models import CollectionAgency, Client, Consumer, Account, AccountConsumer


@admin.register(CollectionAgency)
class CollectionAgencyAdmin(admin.ModelAdmin):
    """Admin configuration for CollectionAgency model."""

    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin configuration for Client model."""

    list_display = ("name", "collection_agency", "created_at")
    list_filter = ("collection_agency",)
    search_fields = ("name",)


@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    """Admin configuration for Consumer model."""

    list_display = ("name", "ssn", "created_at")
    search_fields = ("name", "ssn")


class AccountConsumerInline(admin.TabularInline):
    """Inline admin for AccountConsumer model."""

    model = AccountConsumer
    extra = 1


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin configuration for Account model."""

    list_display = ("client_reference_no", "balance", "status", "client", "created_at")
    list_filter = ("status", "client")
    search_fields = ("client_reference_no",)
    inlines = [AccountConsumerInline]
