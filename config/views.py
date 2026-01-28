from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied

from .models import User, Building, Service, Order, OrderHistory
from .serializers import (
    UserSerializer, BuildingSerializer, ServiceSerializer,
    OrderSerializer, OrderHistorySerializer
)


from django.shortcuts import render
from .models import Order, User, Building
# -------------------
# API Root
# -------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        '1. Имараттар (Buildings)': reverse('building-list', request=request, format=format),
        '2. Менеджерлер (Managers)': reverse('manager-list', request=request, format=format),
        '3. Кызматтар (Services)': reverse('service-list', request=request, format=format),
        '4. Кардарлар (Clients)': reverse('client-list', request=request, format=format),
        '5. Заказдар (Orders)': reverse('order-list', request=request, format=format),
        '6. Заказдардын тарыхы (History)': reverse('orderhistory-list', request=request, format=format),
    })

# -------------------
# User / Manager / Client
# -------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class ManagerViewSet(UserViewSet):
    def get_queryset(self):
        return User.objects.filter(role='MANAGER')

class ClientViewSet(UserViewSet):
    def get_queryset(self):
        return User.objects.filter(role='USER')

# -------------------
# Building / Service
# -------------------
class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

# -------------------
# Order / OrderHistory
# -------------------
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or (hasattr(user, 'role') and user.role == 'ADMIN'):
            return Order.objects.all()
        if hasattr(user, 'role') and user.role == 'MANAGER':
            return Order.objects.filter(building=user.managed_building)
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_anonymous:
            raise PermissionDenied("Сиз логин болушуңуз керек, заказ түзүү үчүн.")
        # Эгер менеджер болсо, анын имараты менен байланыштырабыз
        user_building = getattr(user, 'managed_building', None)
        serializer.save(user=user, building=user_building, status='NEW')

    def perform_update(self, serializer):
        instance = self.get_object()
        old_status = instance.status
        new_order = serializer.save()
        if old_status != new_order.status:
            OrderHistory.objects.create(
                order=new_order,
                old_status=old_status,
                new_status=new_order.status
            )


class OrderHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderHistory.objects.all()
    serializer_class = OrderHistorySerializer
    permission_classes = [permissions.IsAuthenticated]


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, Building, Service, Order

# -------------------
# Dashboard – заказдардын панели
# -------------------
@login_required
def dashboard(request):
    user = request.user
    if hasattr(user, 'role') and user.role == 'ADMIN':
        orders = Order.objects.all()
    elif hasattr(user, 'role') and user.role == 'MANAGER':
        orders = Order.objects.filter(building=user.managed_building)
    else:
        orders = Order.objects.filter(user=user)
    return render(request, 'orders.html', {'orders': orders})

# -------------------
# Clients View
# -------------------
@login_required
def clients_view(request):
    clients = User.objects.filter(role='USER')
    return render(request, 'clients.html', {'clients': clients})

# -------------------
# Buildings View
# -------------------
@login_required
def buildings_view(request):
    buildings = Building.objects.all()
    return render(request, 'buildings.html', {'buildings': buildings})

# -------------------
# Create Order
# -------------------
@login_required
def create_order(request):
    services = Service.objects.all()
    buildings = Building.objects.all()
    if request.method == 'POST':
        service_id = request.POST.get('service')
        building_id = request.POST.get('building')
        date = request.POST.get('date')
        time = request.POST.get('time')
        comment = request.POST.get('comment', '')

        service = Service.objects.get(id=service_id)
        building = Building.objects.get(id=building_id) if building_id else None

        Order.objects.create(
            user=request.user,
            service=service,
            building=building,
            date=date,
            time=time,
            comment=comment
        )
        return redirect('dashboard')

    return render(request, 'create_order.html', {
        'services': services,
        'buildings': buildings
    })




def dashboard(request):
    orders = Order.objects.all()
    return render(request, 'orders.html', {'orders': orders})

def clients_view(request):
    clients = User.objects.filter(role='USER')
    return render(request, 'clients.html', {'clients': clients})

def buildings_view(request):
    buildings = Building.objects.all()
    return render(request, 'buildings.html', {'buildings': buildings})

def create_order(request):
    # Форму жана логика кошо аласың
    return render(request, 'create_order.html')
