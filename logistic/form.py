import re

from django import forms
from .models import *
from django import forms
from django.utils.timezone import now

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['login', 'password', 'role', 'phone']

class DeliveryTimeForm(forms.ModelForm):
    class Meta:
        model = DeliveryTime
        fields = '__all__'
        widgets = {
            'delivery_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'cost', 'address', 'status', 'departure_date', 'delivery_date', 'is_deleted']
        widgets = {
            'departure_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'delivery_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class SupplyOrderForm(forms.Form):
    is_supply = forms.BooleanField(label="Это поставка", required=True)
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="Продукт")
    quantity = forms.IntegerField(label="Количество")
    departure_date = forms.DateField(
        label="Дата отправки",
        initial=now().date,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    delivery_date = forms.DateField(
        label="Дата доставки",
        initial=now().date,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Количество должно быть положительным числом.")
        return quantity


class UserOrderForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_deleted=False))
    quantity = forms.IntegerField(min_value=1)

    def clean_quantity(self):
        product = self.cleaned_data.get('product')
        quantity = self.cleaned_data.get('quantity')
        stock = Stock.objects.filter(product=product).first()

        if stock and stock.quantity < quantity:
            raise forms.ValidationError(f"Недостаточно товара '{product.title}' на складе.")

        return quantity

class RegisterForm(forms.ModelForm):
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")

    class Meta:
        model = User
        fields = ['login', 'password', 'phone']
        widgets = {
            'password': forms.PasswordInput,
        }

    def clean_login(self):
        login = self.cleaned_data.get('login')
        if User.objects.filter(login=login).exists():
            raise forms.ValidationError("Пользователь с таким логином уже существует.")
        return login

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if len(password) < 6:
            raise forms.ValidationError("Пароль должен содержать не менее 6 символов.")
        if not re.search(r'[A-Za-z]', password):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну букву.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну заглавную букву.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Пароли не совпадают")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        client_role, created = Role.objects.get_or_create(role="client")
        user.role = client_role

        if commit:
            user.save()
        return user


class UpdateUserForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput, label="Текущий пароль", required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, label="Новый пароль", required=False)
    new_password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение нового пароля",
                                           required=False)
    phone = forms.CharField(label="Телефон", required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password or new_password_confirm:
            if not current_password:
                self.add_error("current_password", "Вы должны указать текущий пароль.")
            elif not check_password(current_password, self.user.password):
                self.add_error("current_password", "Текущий пароль неверный.")

            if new_password != new_password_confirm:
                self.add_error("new_password_confirm", "Новые пароли не совпадают.")

        return cleaned_data

