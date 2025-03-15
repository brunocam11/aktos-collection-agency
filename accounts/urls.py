from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CollectionAgencyViewSet,
    ClientViewSet,
    ConsumerViewSet,
    AccountViewSet,
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"collection-agencies", CollectionAgencyViewSet)
router.register(r"clients", ClientViewSet)
router.register(r"consumers", ConsumerViewSet)
router.register(r"accounts", AccountViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
