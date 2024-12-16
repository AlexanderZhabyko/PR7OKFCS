import datetime
import random

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

class NonDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def get_by_natural_key(self, login):
        return self.get(login=login)


class Role(models.Model):
    ADMIN = 'admin'
    MANAGER = 'manager'
    DELIVERY = 'delivery'
    CLIENT = 'client'
    WAREHOUSE = 'warehouse'
    PROVIDER = 'provider'

    roles = [
        (ADMIN, 'Administrator'),
        (MANAGER, 'Manager'),
        (DELIVERY, 'Delivery Person'),
        (CLIENT, 'Client'),
        (WAREHOUSE, 'Warehouse Worker'),
        (PROVIDER, 'Provider'),
    ]

    role = models.CharField(max_length=15, choices=roles)
    is_deleted = models.BooleanField(default=False)

    objects = NonDeletedManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.role


class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^[0-9\(\)\-\+]+$',
                message="Телефон может содержать только цифры, знаки (), -, +.",
            )
        ])
    is_deleted = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['phone', 'role']

    objects = NonDeletedManager()
    all_objects = models.Manager()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        action = 'Created' if is_new else 'Updated'
        Log.objects.create(user=self, action=action, description=f'user {self.login}', is_deleted=False)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
        Log.objects.create(user=self, action='Deleted', description=f'user {self.login}', is_deleted=False)

    def __str__(self):
        return self.login


class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)

    objects = NonDeletedManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.user.login} - {self.action}"


class Provider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    product_type = models.CharField(max_length=20)
    is_deleted = models.BooleanField(default=False)

    objects = NonDeletedManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        action = 'Created' if is_new else 'Updated'
        Log.objects.create(user=self.user, action=action, description=f'provider {self.id}', is_deleted=False)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
        Log.objects.create(user=self.user, action='Deleted', description=f'provider {self.id}',
                           is_deleted=False)

    def __str__(self):
        return f"Provider {self.id} - {self.user.login}"


class Product(models.Model):
    title = models.CharField(max_length=20)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    weight = models.FloatField()
    price = models.FloatField()
    is_deleted = models.BooleanField(default=False)

    objects = NonDeletedManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        action = 'Created' if is_new else 'Updated'
        Log.objects.create(user=self.provider.user, action=action, description=f'product {self.title}',
                           is_deleted=False)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
        Log.objects.create(user=self.provider.user, action='Deleted', description=f'product {self.title}',
                           is_deleted=False)

    def __str__(self):
        return self.title


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    line = models.IntegerField()
    cell = models.IntegerField()
    quantity = models.IntegerField()
    min_quantity = models.IntegerField(default=10)
    is_deleted = models.BooleanField(default=False)

    objects = NonDeletedManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if self.quantity < self.min_quantity:
            self.create_supply()

        action = 'Created' if is_new else 'Updated'
        Log.objects.create(user=self.product.provider.user, action=action,
                           description=f'product {self.product.title}', is_deleted=False)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
        Log.objects.create(user=self.product.provider.user, action='Deleted',
                           description=f'product {self.product.title}', is_deleted=False)

    def create_supply(self):
        missing_quantity = self.min_quantity - self.quantity + 5
        if missing_quantity <= 0:
            return

        supply_status, created = OrderStatus.objects.get_or_create(status="Поставка")
        order = Order.objects.create(
            user=self.product.provider.user,
            cost=0,
            is_supply=True,
            status=supply_status,
            departure_date=datetime.date.today(),
            delivery_date=datetime.date.today() + datetime.timedelta(days=1),
        )

        ProductOrder.objects.create(order=order, product=self.product, quantity=missing_quantity)

        self.quantity += missing_quantity
        super().save(update_fields=['quantity'])

        print(f"Создана автоматическая поставка для {self.product.title}, добавлено: {missing_quantity}")

    def __str__(self):
        return f"Stock of {self.product.title} at line {self.line}, cell {self.cell}"


class OrderStatus(models.Model):
    status = models.CharField(max_length=20)
    is_deleted = models.BooleanField(default=False)

    objects = NonDeletedManager()
    all_objects = models.Manager()

    def save(self, user=None, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        action = 'Created' if is_new else 'Updated'

        if user:
            Log.objects.create(
                user=user,
                action=action,
                description=f'Order status {self.status}',
                is_deleted=False
            )

    def delete(self, user=None, *args, **kwargs):
        self.is_deleted = True
        self.save()

        if user:
            Log.objects.create(
                user=user,
                action='Deleted',
                description=f'Order status {self.status}',
                is_deleted=False
            )

    def __str__(self):
        return self.status

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cost = models.FloatField()
    address = models.CharField(max_length=50)
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    tracking_number = models.IntegerField(blank=True, null=True)
    departure_date = models.DateTimeField(default=datetime.date.today())
    delivery_date = models.DateTimeField(null = True, blank = True)
    is_deleted = models.BooleanField(default=False)
    is_supply = models.BooleanField(default=False, verbose_name="Поставка")


    objects = NonDeletedManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = random.randint(10000000, 99999999)
        is_new = self.pk is None
        super().save(*args, **kwargs)

        action = 'Created' if is_new else 'Updated'
        Log.objects.create(user=self.user, action=action, description=f'order {self.id}', is_deleted=False)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
        Log.objects.create(user=self.user, action='Deleted', description=f'order {self.id}', is_deleted=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.login}"


class ProductOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_deleted = models.BooleanField(default=False)

    objects = NonDeletedManager()
    all_objects = models.Manager()

    def clean(self):
        stock = Stock.objects.filter(product=self.product).first()
        if stock and stock.quantity < self.quantity:
            raise ValidationError(f"Недостаточно товара '{self.product.title}' на складе.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.clean()
        super().save(*args, **kwargs)

        action = 'Created' if is_new else 'Updated'
        Log.objects.create(user=self.order.user, action=action,
                           description=f'product {self.product.title} in order {self.order.id}',
                           is_deleted=False)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
        Log.objects.create(user=self.order.user, action='Deleted',
                           description=f'product {self.product.title} in order {self.order.id}',
                           is_deleted=False)

    def __str__(self):
        return f"Product {self.product.title} in Order {self.order.id}"


class DeliveryTime(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    delivery_time = models.DateField()
    quantity = models.IntegerField()
    is_deleted = models.BooleanField(default=False)

    objects = NonDeletedManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        action = 'Created' if is_new else 'Updated'
        Log.objects.create(user=self.provider.user, action=action,
                           description=f'delivery for product {self.product.title} by {self.provider.user.login}',
                           is_deleted=False)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
        Log.objects.create(user=self.provider.user, action='Deleted',
                           description=f'delivery for product {self.product.title} by {self.provider.user.login}',
                           is_deleted=False)

    def __str__(self):
        return f"Delivery of {self.product.title} by {self.provider.user.login} at {self.delivery_time}"
