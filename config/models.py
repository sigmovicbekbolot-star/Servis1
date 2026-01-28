from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# 1. Колдонуучу жана Менеджер (Бир таблицада, ролдору менен)
class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('USER', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
    phone = models.CharField(max_length=20, null=True, blank=True)
    managed_building = models.ForeignKey(
        'Building',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Django кагылышууну алдын алуу үчүн
    groups = models.ManyToManyField(
        Group,
        related_name='config_user_set',  # уникальное имя
        blank=True,
        help_text='Группы пользователя.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='config_user_permissions_set',  # уникальное имя
        blank=True,
        help_text='Разрешения пользователя.',
        verbose_name='user permissions'
    )

# 2. Имарат
class Building(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    image = models.ImageField(upload_to='buildings/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 3. Кызмат
class Service(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 4. Заказ
class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Ожидания'),        # заказ күтүлүүдө
        ('IN_PROGRESS', 'В процессе'),  # аткарылып жатат
        ('DONE', 'Выполнено'),      # аткарылды
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"


# 5. Заказдардын тарыхы (Order History)
class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history_logs')
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    change_date = models.DateTimeField(auto_now_add=True)
