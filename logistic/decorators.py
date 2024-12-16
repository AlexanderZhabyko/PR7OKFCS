from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from logistic.models import Role


def role_required(role_names):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Для доступа к этой странице необходимо войти в систему.")
                return redirect('home')

            if not request.user.role or request.user.role.role not in role_names:
                messages.warning(request, "У вас нет доступа к этой странице.")
                previous_url = request.META.get('HTTP_REFERER', reverse('home'))
                return redirect(previous_url)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def admin_required(view_func):
    return role_required(['admin'])(view_func)