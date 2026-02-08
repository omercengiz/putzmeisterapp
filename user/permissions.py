# user/permissions.py
from functools import wraps
from django.shortcuts import redirect, render

def get_user_role(user):
    if user.is_superuser:
        return "admin"
    return getattr(getattr(user, "role_info", None), "role", None)


def admin_only(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("user:login")

        if get_user_role(request.user) == "admin":
            return view_func(request, *args, **kwargs)

        return render(request, "403.html", status=403)
    return wrapper


def write_access_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("user:login")

        role = get_user_role(request.user)

        # ❗ Viewer kesinlikle geçemez
        if role in ("admin", "editor"):
            return view_func(request, *args, **kwargs)

        return render(request, "403.html", status=403)
    return wrapper
