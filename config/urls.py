from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    api_root, UserViewSet, ManagerViewSet, ClientViewSet,
    BuildingViewSet, ServiceViewSet, OrderViewSet, OrderHistoryViewSet,
    home, service_detail, signup, RegisterView
)
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

# Swagger үчүн керектүү импорттор
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# -------------------
# API роутер
# -------------------
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'buildings', BuildingViewSet, basename='building')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'orderhistories', OrderHistoryViewSet, basename='orderhistory')

# -------------------
# URL паттерндер
# -------------------
urlpatterns = [
    # ===================
    # ТИЛДИ КОТОРУУ (ЖАҢЫ!)
    # ===================
    # Бул сап баскычты басканда тилди алмаштырууга жооп берет
    path('i18n/', include('django.conf.urls.i18n')),

    # ===================
    # БАШКЫ БЕТ
    # ===================
    path('', views.home, name='home'),
    path('service/<int:pk>/', views.service_detail, name='service_detail'),

    # ===================
    # АВТОРИЗАЦИЯ (HTML)
    # ===================
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # Django 5.0+ үчүн logout POST-запрос менен иштеши керек, аны base.html'де жасадык
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup, name='signup'),

    # ===================
    # HTML ИНТЕРФЕЙС (ПАНЕЛЬ ЖАНА БАШКАРУУ)
    # ===================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('clients/', views.clients_view, name='clients'),
    path('buildings/', views.buildings_view, name='buildings'),

    # Заказдар
    path('create_order/', views.create_order, name='create_order'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/<int:pk>/delete/', views.order_delete, name='order_delete'),
    path('order/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('order/<int:pk>/status/<str:status>/', views.update_order_status, name='update_status'),

    # ТӨЛӨМ БАРАГЫ
    path('order/<int:pk>/payment/', views.payment_page, name='payment_page'),

    # Кардарлар
    path('clients/add/', views.client_create, name='client_create'),
    path('client/<int:pk>/', views.client_detail, name='client_detail'),
    path('client/<int:pk>/edit/', views.client_edit, name='client_edit'),

    # ===================
    # API ИНТЕРФЕЙС
    # ===================
    path('api/', api_root, name='api-root'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/', include(router.urls)),

    # ===================
    # SWAGGER / API DOCS
    # ===================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Сүрөттөр (media) үчүн жол
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)