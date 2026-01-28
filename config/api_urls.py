from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    UserViewSet, ManagerViewSet, ClientViewSet,
    BuildingViewSet, ServiceViewSet, OrderViewSet, OrderHistoryViewSet, api_root
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'buildings', BuildingViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'orderhistories', OrderHistoryViewSet, basename='orderhistory')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
]
