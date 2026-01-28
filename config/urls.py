from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    api_root, UserViewSet, ManagerViewSet, ClientViewSet,
    BuildingViewSet, ServiceViewSet, OrderViewSet, OrderHistoryViewSet
)
from . import views

# -------------------
# API роутер
# -------------------
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'buildings', BuildingViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'orderhistories', OrderHistoryViewSet, basename='orderhistory')

# -------------------
# URL паттерндер
# -------------------
urlpatterns = [
    # HTML интерфейс
    path('', views.dashboard, name='dashboard'),
    path('clients/', views.clients_view, name='clients'),
    path('buildings/', views.buildings_view, name='buildings'),
    path('create_order/', views.create_order, name='create_order'),

    # API интерфейс
    path('api/', include(router.urls)),  # ✅ API роут кошулду
]