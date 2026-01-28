from rest_framework import serializers
from .models import User, Building, Service, Order, OrderHistory

# Кардарлар жана менеджерлер үчүн serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone')
        read_only_fields = ('id',)

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'date', 'time', 'status', 'comment', 'created_at', 'user', 'service', 'building')


class OrderHistorySerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    old_status = serializers.SerializerMethodField()
    new_status = serializers.SerializerMethodField()

    class Meta:
        model = OrderHistory
        fields = ('id', 'order', 'old_status', 'new_status', 'change_date')

    STATUS_DISPLAY = {
        'NEW': 'Ожидания',
        'PENDING': 'Ожидания',  # PENDING орусча
        'IN_PROGRESS': 'В процессе',
        'DONE': 'Выполнено',
    }

    def get_old_status(self, obj):
        return self.STATUS_DISPLAY.get(obj.old_status, obj.old_status)

    def get_new_status(self, obj):
        return self.STATUS_DISPLAY.get(obj.new_status, obj.new_status)

