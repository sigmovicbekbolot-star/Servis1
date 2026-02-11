from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


# 1. User модели
class User(AbstractUser):
    ROLE_CHOICES = [('ADMIN', 'Admin'), ('MANAGER', 'Manager'), ('USER', 'User')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    managed_building = models.ForeignKey('Building', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='managers')

    groups = models.ManyToManyField(Group, related_name='config_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='config_user_permissions_set', blank=True)

    class Meta:
        verbose_name = "Колдонуучу"
        verbose_name_plural = "Колдонуучулар"


# 2. Category модели
class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default="fa-tools")
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категориялар"

    def __str__(self): return self.name


# 3. Building модели
class Building(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    image = models.ImageField(upload_to='buildings/', null=True, blank=True)

    class Meta:
        verbose_name = "Имарат"
        verbose_name_plural = "Имараттар"

    def __str__(self): return self.name


# 4. Service модели
class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='services')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='services/', null=True, blank=True)

    def get_average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0

    class Meta:
        verbose_name = "Кызмат"
        verbose_name_plural = "Кызматтар"

    def __str__(self): return self.name


# 5. Order модели
class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Жаңы'),
        ('WAITING_PAYMENT', 'Төлөм күтүлүүдө'),
        ('PAID', 'Төлөндү'),
        ('IN_PROGRESS', 'Аткарылууда'),
        ('DONE', 'Аяктады'),
        ('CANCELLED', 'Жокко чыгарылды'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, null=True, blank=True, on_delete=models.SET_NULL)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prepayment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Бааны автоматтык түрдө кызматтан алуу
        if not self.total_price and self.service:
            self.total_price = self.service.price

        # Взнос суммасын (10%) эсептөө
        if self.total_price:
            from decimal import Decimal
            self.prepayment_amount = self.total_price * Decimal('0.10')

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказдар"


# 6. Review модели
class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Пикир"
        verbose_name_plural = "Пикирлер"


# 7. OrderHistory модели
class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history_logs')
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    change_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Заказ тарыхы"
        verbose_name_plural = "Заказ тарыхы"


# 8. Client модели
class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        verbose_name = "Кардар"
        verbose_name_plural = "Кардарлар"