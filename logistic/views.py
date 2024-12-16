import json
import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.paginator import Paginator
from django.forms import modelform_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .decorators import role_required
from .form import *
from .models import *


# Create your views here.

def home(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('login')
        else:
            messages.error(request, "Ошибка регистрации. Проверьте данные.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == "POST":
        login_input = request.POST.get('login')
        password_input = request.POST.get('password')

        user = authenticate(request, username=login_input, password=password_input)

        if user is not None:
            login(request, user)
            logger.info(f'Пользователь {login_input} успешно вошел в систему')
            if user.role.role == 'client':
                return redirect('account_view')
            else:
                return redirect('home')
        else:
            logger.warning(f'Неудачная попытка входа для пользователя {login_input}')
            messages.error(request, "Неверный логин или пароль")
            return render(request, 'login.html')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')

@login_required
@role_required(['admin'])
def logs_list(request):
    query = request.GET.get('search', '')

    if query:
        logs = Log.objects.filter(user__login__icontains=query).order_by('-id')
    else:
        logs = Log.objects.all().order_by('-id')

    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'logs.html', {'page_obj': page_obj, 'search_query': query})

@login_required
@role_required(['admin'])
def users_list(request):
    logs = User.objects.all()
    paginator = Paginator(logs, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'users.html', {'page_obj': page_obj})

@login_required
@role_required(['admin'])
def add_user(request):
    exclude_fields = ['last_login', 'is_staff', 'is_superuser', 'groups', 'user_permissions']
    return add_object(request, User, 'User', exclude_fields=exclude_fields)
@login_required
@role_required(['admin'])
def edit_user(request, pk):
    exclude_fields = ['last_login', 'is_staff', 'is_superuser', 'groups', 'user_permissions']
    return edit_object(request, User, 'user', pk, exclude_fields=exclude_fields)
@login_required
@role_required(['admin'])
def delete_user(request, pk):
    return delete_object(request, User, pk, 'users_list')

@login_required
@role_required(['warehouse', 'admin'])
def stocks_list(request):
    logs = Stock.objects.all()
    paginator = Paginator(logs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'stock.html', {'page_obj': page_obj})

@login_required
@role_required(['warehouse', 'admin'])
def add_stock(request):
    return add_object(request, Stock, 'Stock')
@login_required
@role_required(['warehouse', 'admin'])
def edit_stock(request, pk):
    return edit_object(request, Stock, 'Stock', pk)
@login_required
@role_required(['warehouse', 'admin'])
def delete_stock(request, pk):
    return delete_object(request, Stock, pk, 'stocks_list')
@login_required
@role_required(['admin'])
def roles_list(request):
    logs = Role.objects.all()
    paginator = Paginator(logs, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'roles.html', {'page_obj': page_obj})

@login_required
@role_required(['admin'])
def add_roles(request):
    return add_object(request, Role, 'Role')

@login_required
@role_required(['admin'])
def edit_roles(request, pk):
    return edit_object(request, Role, 'Role', pk)

@login_required
@role_required(['admin'])
def delete_role(request, pk):
    return delete_object(request, Role, pk, 'roles_list')

@login_required
@role_required(['admin', 'manager', 'provider'])
def providers_list(request):
    logs = Provider.objects.all()
    paginator = Paginator(logs, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'providers.html', {'page_obj': page_obj})

@login_required
@role_required(['admin', 'manager'])
def add_providers(request):
    return add_object(request, Provider, 'Provider')
@login_required
@role_required(['admin', 'manager'])
def edit_providers(request, pk):
    return edit_object(request, Provider, 'Provider', pk)
@login_required
@role_required(['admin', 'manager'])
def delete_provider(request, pk):
    return delete_object(request, Provider, pk, 'providers_list')
@login_required
@role_required(['client', 'manager', 'admin'])
def products_list(request):
    logs = Product.objects.all()
    paginator = Paginator(logs, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'product.html', {'page_obj': page_obj})

@login_required
@role_required(['manager', 'admin'])
def add_product(request):
    return add_object(request, Product, 'Product')
@login_required
@role_required(['manager', 'admin'])
def edit_product(request, pk):
    return edit_object(request, Product, 'Product', pk)
@login_required
@role_required(['manager', 'admin'])
def delete_product(request, pk):
    return delete_object(request, Product, pk, 'products_list')

@login_required
@role_required(['client', 'manager', 'admin'])
def productorders_list(request):
    logs = ProductOrder.objects.all()
    paginator = Paginator(logs, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'producrOrders.html', {'page_obj': page_obj})
@login_required
@role_required(['manager', 'admin'])
def add_productorders(request):
    return add_object(request, ProductOrder, 'ProductOrder')

@login_required
@role_required(['manager', 'admin'])
def edit_productorders(request, pk):
    return edit_object(request, ProductOrder, 'ProductOrder', pk)
@login_required
@role_required(['manager', 'admin'])
def delete_productorders(request, pk):
    return delete_object(request, ProductOrder, pk, 'productorders_list')

@login_required
@role_required(['manager', 'admin', 'delivery'])
def orders_list(request):
    query = request.GET.get('search', '')

    if query:
        logs = Order.objects.filter(user__login__icontains=query)
    else:
        logs = Order.objects.all()
    paginator = Paginator(logs, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'orders.html', {'page_obj': page_obj})

@login_required
@role_required(['manager', 'admin'])
def add_orders(request):
    return add_object(request, Order, 'Order', exclude_fields=['tracking_number'])

@login_required
@role_required(['manager', 'admin'])
def edit_orders(request, pk):
    return edit_object(request, Order, 'Order', pk, exclude_fields=['tracking_number'])

@login_required
@role_required(['manager', 'admin'])
def delete_orders(request, pk):
    return delete_object(request, Order, pk, 'orders_list')

@login_required
@role_required(['manager', 'admin', 'delivery'])
def delivery_times_list(request):
    logs = DeliveryTime.objects.all()
    paginator = Paginator(logs, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'deliveryTime.html', {'page_obj': page_obj})

@login_required
@role_required(['manager', 'admin', 'delivery'])
def add_delivery_time(request):
    return add_object(request, DeliveryTime, 'Delivery_Time')

@login_required
@role_required(['manager', 'admin', 'delivery'])
def edit_delivery_time(request, pk):
    return edit_object(request, DeliveryTime, 'Delivery_Time', pk)

@login_required
@role_required(['manager', 'admin',])
def delete_delivery_time(request, pk):
    return delete_object(request, DeliveryTime, pk, 'delivery_times_list')

@login_required
@role_required(['manager', 'admin'])
def order_statuss_list(request):
    logs = OrderStatus.objects.all()
    paginator = Paginator(logs, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'orderStatus.html', {'page_obj': page_obj})

@login_required
@role_required(['manager', 'admin'])
def add_order_status(request):
    return add_object(request, OrderStatus, 'Order_Status')

@login_required
@role_required(['manager', 'admin'])
def edit_order_status(request, pk):
    return edit_object(request, OrderStatus, 'Order_Status', pk)

@login_required
@role_required(['manager', 'admin'])
def delete_order_status(request, pk):
    return delete_object(request, OrderStatus, pk, 'order_statuss_list')


def add_object(request, model_class, model_name, exclude_fields=None):
    form_class = modelform_factory(model_class, exclude=exclude_fields or [])

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(model_name.lower() + 's_list')
    else:
        form = form_class()

    return render(request, 'form_add.html', {'form': form, 'model_name': model_name})

def edit_object(request, model_class, model_name, pk, exclude_fields=None):
    obj = model_class.objects.get(pk=pk)
    form_class = modelform_factory(model_class, exclude=exclude_fields or [])

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(model_name.lower() + 's_list')
    else:
        form = form_class(instance=obj)

    return render(request, 'form_edit.html', {'form': form, 'model_name': model_name})

def delete_object(request, model_class, pk, redirect_url):
    obj = get_object_or_404(model_class, pk=pk)
    obj.delete()
    return redirect(redirect_url)


@login_required
@role_required(['admin', 'provider'])
def create_supply(request):
    print(f"Is authenticated: {request.user.is_authenticated}")
    print(f"Current user: {request.user}")

    if request.method == 'POST':
        form = SupplyOrderForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']

            supply_status, created = OrderStatus.objects.get_or_create(status="Поставка")
            print(f"Supply status: {supply_status}, created: {created}")

            departure_date = form.cleaned_data.get('departure_date', datetime.date.today())
            delivery_date = form.cleaned_data.get('delivery_date', departure_date + datetime.timedelta(days=1))
            order = Order.objects.create(
                user=request.user,
                cost=0,
                is_supply=True,
                status=supply_status,
                departure_date=departure_date,
                delivery_date=delivery_date,
            )
            print(f"Created supply order: {order}")

            ProductOrder.objects.create(order=order, product=product, quantity=quantity)
            print(f"Product added to order: {product.title}, quantity: {quantity}")

            stock, created = Stock.objects.get_or_create(product=product)
            stock.quantity += quantity
            stock.save()
            print(f"Stock updated for product: {product.title}, new quantity: {stock.quantity}")

            return redirect('orders_list')
        else:
            print("Form is invalid")
            print(form.errors)
    else:
        form = SupplyOrderForm()

    return render(request, 'add_supply.html', {'form': form})

@login_required
@role_required(['manager', 'admin', 'provider', 'warehouse', 'delivery', 'client'])
def user_create_order(request):
    if request.method == 'POST':
        form = UserOrderForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            status, created = OrderStatus.objects.get_or_create(status__iexact="Принят в работу")

            departure_date = datetime.date.today()
            delivery_date = None
            print(f"Departure date: {departure_date}")
            print(f"Delivery date: {delivery_date}")

            order = Order.objects.create(
                user=request.user,
                cost=product.price * quantity,
                address=request.user.phone,
                status=status,
                departure_date=departure_date,
                delivery_date=delivery_date,
            )

            ProductOrder.objects.create(order=order, product=product, quantity=quantity)

            stock = Stock.objects.filter(product=product).first()
            if stock is not None:
                if stock.quantity >= quantity:
                    stock.quantity -= quantity
                    stock.save()
                else:
                    form.add_error(None, "Недостаточное количество товара на складе.")
                    return render(request, 'user_order.html', {'form': form})
            else:
                form.add_error(None, "Товар отсутствует на складе.")
                return render(request, 'user_order.html', {'form': form})

            return redirect('account_view')
    else:
        form = UserOrderForm()

    return render(request, 'user_order.html', {'form': form})

def backup_database(request):
    backup_data = {
        "Role": serializers.serialize('json', Role.objects.all()),
        "User": serializers.serialize('json', User.objects.all()),
        "Log": serializers.serialize('json', Log.objects.all()),
        "Provider": serializers.serialize('json', Provider.objects.all()),
        "Product": serializers.serialize('json', Product.objects.all()),
        "Stock": serializers.serialize('json', Stock.objects.all()),
        "OrderStatus": serializers.serialize('json', OrderStatus.objects.all()),
        "Order": serializers.serialize('json', Order.objects.all()),
        "ProductOrder": serializers.serialize('json', ProductOrder.objects.all()),
        "DeliveryTime": serializers.serialize('json', DeliveryTime.objects.all()),
    }

    response = HttpResponse(json.dumps(backup_data, indent=4), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="backup.json"'
    return response

def restore_database(request):
    if request.method == "POST" and request.FILES.get("backup_file"):
        backup_file = request.FILES["backup_file"]
        try:
            backup_data = json.load(backup_file)
            for model_name, model_data in backup_data.items():
                for obj in serializers.deserialize("json", model_data):
                    obj.save()
            messages.warning(request,
             "База данных успешно восстановлена. Обратите внимание: восстановление могло затронуть существующие данные.")
            return HttpResponse("База данных успешно восстановлена.")
        except Exception as e:
            return HttpResponse(f"Ошибка при восстановлении базы данных: {str(e)}", status=500)

    return HttpResponse("Необходимо загрузить файл резервной копии.", status=400)

@login_required
def account_view(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.user, request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            new_password = form.cleaned_data.get('new_password')

            if phone:
                request.user.phone = phone

            if new_password:
                request.user.set_password(new_password)

            request.user.save()
            messages.success(request, "Данные успешно обновлены.")
            return redirect('login')
    else:
        form = UpdateUserForm(request.user, initial={"phone": request.user.phone})

    orders = Order.objects.filter(user=request.user, is_deleted=False)
    return render(request, 'account.html', {'orders': orders, 'form': form})


@login_required
@role_required(['manager', 'admin', 'delivery'])
def delivery_orders(request):

    delivery_status = OrderStatus.objects.filter(status="Доставка").first()
    if delivery_status:
        orders = Order.objects.filter(status=delivery_status)
    else:
        orders = []

    return render(request, 'account_delivery.html', {'orders': orders})

@login_required
@role_required(['manager', 'delivery'])
def mark_as_delivered(request, order_id):
    order = Order.objects.get(id=order_id)
    if order.status.status == "Доставка":
        delivered_status, created = OrderStatus.objects.get_or_create(status="Выдан")
        order.status = delivered_status
        order.delivery_date = datetime.datetime.now()
        order.save()
        return redirect('delivery_orders')
    return redirect('delivery_orders')