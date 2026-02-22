from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/admin-panel/login/')
        if not (request.user.is_admin or request.user.is_staff):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper
