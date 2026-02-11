from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.utils import timezone

# Моделдер жана Сериализаторлор
from .models import User, Building, Service, Order, OrderHistory, Client, Category, Review
from .serializers import (
    UserSerializer, BuildingSerializer, ServiceSerializer,
    OrderSerializer, OrderHistorySerializer, RegisterSerializer
)

# =========================================================
# 1. АВТОРИЗАЦИЯ ЖАНА РЕГИСТРАЦИЯ (HTML & API)
# =========================================================

# Бул жерде ListCreateAPIView колдонобуз, ошондо API аркылуу катталгандарды GET менен көрсө болот
class RegisterView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    # Катталгандан кийин колдонуучунун ролун автоматтык түрдө 'USER' кылабыз
    def perform_create(self, serializer):
        user = serializer.save()
        user.role = 'USER'
        user.save()


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # Маалыматты убактылуу кармайбыз
            user.role = 'USER'             # Ролун бекитебиз
            user.save()                    # Эми базага "тарс" деп сактайбыз
            login(request, user)
            messages.success(request, "Каттоо ийгиликтүү өттү! Кош келиңиз.")
            return redirect('home')
        else:
            # Эгер ката болсо, колдонуучуга эмне ката экенин көрсөтөбүз
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


# =========================================================
# 2. ФОРМАЛАР
# =========================================================

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['service', 'building', 'status']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


# =========================================================
# 3. HTML VIEWS (БАШКЫ БЕТ ЖАНА КЫЗМАТТАР)
# =========================================================

@login_required
def home(request):
    categories = Category.objects.all()
    services = Service.objects.all().prefetch_related('reviews')

    search_query = request.GET.get('search')
    if search_query:
        services = services.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    category_id = request.GET.get('category')
    if category_id:
        services = services.filter(category_id=category_id)

    return render(request, 'home.html', {'categories': categories, 'services': services})


@login_required
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    reviews = service.reviews.all().order_by('-created_at')

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.service = service
            review.user = request.user
            review.save()
            messages.success(request, "Пикириңиз ийгиликтүү кошулду!")
            return redirect('service_detail', pk=service.id)
        else:
            messages.error(request, "Ката кетти. Сураныч, баарын туура толтуруңуз.")
    else:
        form = ReviewForm()

    return render(request, 'service_detail.html', {
        'service': service,
        'reviews': reviews,
        'form': form  # Форманы шаблонго жиберебиз
    })


# =========================================================
# 4. ЗАКАЗДАР ЖАНА ПРЕДОПЛАТА
# =========================================================

@login_required
def create_order(request):
    services = Service.objects.all()
    buildings = Building.objects.all()
    selected_service_id = request.GET.get('service')

    if request.method == 'POST':
        service_id = request.POST.get('service')
        building_id = request.POST.get('building')
        comment = request.POST.get('comment', '')

        service = get_object_or_404(Service, id=service_id)

        order = Order.objects.create(
            user=request.user,
            service=service,
            building=get_object_or_404(Building, id=building_id),
            date=request.POST.get('date') or timezone.now().date(),
            time=request.POST.get('time') or timezone.now().time(),
            comment=comment,
            status='WAITING_PAYMENT'
        )

        messages.info(request, f"Заказ түзүлдү. Активдештирүү үчүн {order.prepayment_amount} сом взнос төлөңүз.")
        return redirect('payment_page', pk=order.id)

    return render(request, 'create_order.html', {
        'services': services, 'buildings': buildings,
        'selected_service_id': selected_service_id
    })


@login_required
def payment_page(request, pk):
    order = get_object_or_404(Order, pk=pk)
    old_display = order.get_status_display()

    if request.method == 'POST':
        order.status = 'PAID'
        order.save()

        # Тарыхка кыргызча жазуу (Төлөндү)
        OrderHistory.objects.create(
            order=order,
            old_status=old_display,
            new_status='Төлөндү',
            changed_by=request.user
        )
        messages.success(request, "Взнос кабыл алынды! Заказ аткарылууга берилди.")
        return redirect('dashboard')

    return render(request, 'payment.html', {'order': order, 'prepayment': order.prepayment_amount})


# =========================================================
# 5. ПАНЕЛЬ ЖАНА БАШКАРУУ (DASHBOARD)
# =========================================================

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'ADMIN':
        orders = Order.objects.all()
    elif user.role == 'MANAGER':
        orders = Order.objects.filter(building=user.managed_building)
    else:
        orders = Order.objects.filter(user=user)
    return render(request, 'orders.html', {'orders': orders.order_by('-created_at')})


@login_required
def update_order_status(request, pk, status):
    order = get_object_or_404(Order, pk=pk)
    if (request.user.role == 'MANAGER' and order.building == request.user.managed_building) or request.user.role == 'ADMIN':
        old_status = order.get_status_display()
        order.status = status
        order.save()
        OrderHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=order.get_status_display(),
            changed_by=request.user
        )
        messages.success(request, f"Заказ статусу жаңыртылды!")
    else:
        messages.error(request, "Сизге бул аракетке уруксат жок!")
    return redirect('dashboard')


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    history = OrderHistory.objects.filter(order=order).order_by('-change_date')
    return render(request, 'order_detail.html', {'order': order, 'history': history})


@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.delete()
        messages.warning(request, "Заказ өчүрүлдү!")
        return redirect('dashboard')
    return render(request, 'order_confirm_delete.html', {'order': order})


@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    old_status_display = order.get_status_display()
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save()
            new_status_display = updated_order.get_status_display()
            if old_status_display != new_status_display:
                OrderHistory.objects.create(
                    order=updated_order,
                    old_status=old_status_display,
                    new_status=new_status_display,
                    changed_by=request.user
                )
            messages.success(request, "Заказ ийгиликтүү жаңыланды!")
            return redirect('order_detail', pk=order.id)
    else:
        form = OrderForm(instance=order)
    return render(request, 'order_form.html', {'form': form, 'order': order})


# =========================================================
# 6. КАРДАРЛАР ЖАНА ИМАРАТТАР
# =========================================================

@login_required
def clients_view(request):
    clients = Client.objects.all()
    return render(request, 'clients.html', {'clients': clients})


@login_required
def buildings_view(request):
    buildings = Building.objects.all()
    return render(request, 'buildings.html', {'buildings': buildings})


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'client_detail.html', {'client': client})


@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.first_name = request.POST.get('first_name')
        client.last_name = request.POST.get('last_name')
        client.phone = request.POST.get('phone')
        client.email = request.POST.get('email')
        client.save()
        messages.success(request, "Кардардын маалыматы ийгиликтүү жаңыртылды!")
        return redirect('client_detail', pk=client.pk)
    return render(request, 'client_form.html', {'client': client})


@login_required
def client_create(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        if first_name and phone:
            Client.objects.create(first_name=first_name, last_name=last_name, phone=phone, email=email)
            messages.success(request, "Жаңы кардар кошулду!")
            return redirect('clients_view') # clients_view'ге редирект
    return render(request, 'client_form.html')


# =========================================================
# 7. API БӨЛҮМҮ (REST FRAMEWORK - ТОЛУК)
# =========================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        '0. Катталуу': reverse('register', request=request, format=format),
        '1. Имараттар': reverse('building-list', request=request, format=format),
        '2. Менеджерлер': reverse('manager-list', request=request, format=format),
        '3. Кызматтар': reverse('service-list', request=request, format=format),
        '4. Кардарлар': reverse('client-list', request=request, format=format),
        '5. Заказдар': reverse('order-list', request=request, format=format),
        '6. Тарых': reverse('orderhistory-list', request=request, format=format),
    })


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ManagerViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return User.objects.filter(role='MANAGER')


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = UserSerializer # Же ClientSerializer
    permission_classes = [permissions.IsAuthenticated]


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.is_staff:
            return Order.objects.all()
        if user.role == 'MANAGER':
            return Order.objects.filter(building=user.managed_building)
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='NEW')

    def perform_update(self, serializer):
        instance = self.get_object()
        old_status = instance.status
        new_order = serializer.save()
        if old_status != new_order.status:
            OrderHistory.objects.create(order=new_order, old_status=old_status, new_status=new_order.status)


class OrderHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderHistory.objects.all()
    serializer_class = OrderHistorySerializer
    permission_classes = [permissions.IsAuthenticated]