from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm, CreateUserForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import UserRole
from functools import wraps
from .permissions import admin_only, get_user_role


def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")

        newUser = User(username=username)
        newUser.set_password(password)
        newUser.save()
        login(request, newUser)
        messages.success(request, "You registered, successfully...")
        return redirect("index")
        
    context = {"form": form}
    return render(request, "register.html", context)


def loginUser(request):
    form = LoginForm(request.POST or None)
    context = {"form": form}
    
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        
        if user is None:
            messages.info(request, "Username or password is wrong...")
            return render(request, "login.html", context)

        messages.success(request, "You logged in successfully...")
        login(request, user)
        return redirect("index")
    
    return render(request, "login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("user:login")


@login_required
@admin_only
def update_user_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Root kullanıcısının rolü değiştirilemez
    if user.username.lower() == 'root' or user.id == 1:
        messages.warning(request, "Root user's role cannot be changed.")
        return redirect('user:user_permission_dashboard')
    
    if request.method == 'POST':
        role = request.POST.get('role')
        
        if role in dict(UserRole.ROLE_CHOICES):
            # Admin rolü sadece admin tarafından atanabilir (zaten @admin_only var ama açıklık için)
            if role == 'admin' and get_user_role(request.user) != 'admin':
                messages.warning(request, "Only admins can assign admin role.")
                return redirect('user:user_permission_dashboard')
            
            UserRole.objects.update_or_create(user=user, defaults={'role': role})
            messages.success(request, f"Role updated successfully for '{user.username}'.")
        else:
            messages.error(request, "Invalid role selected.")
    
    return redirect('user:user_permission_dashboard')


@admin_only
def create_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_obj = get_object_or_404(User, pk=user_id) if user_id else None

        # Root kullanıcısı düzenlenemez
        if user_obj and (user_obj.username.lower() == 'root' or user_obj.id == 1):
            messages.warning(request, "Root user cannot be edited.")
            return redirect('user:user_permission_dashboard')

        form = CreateUserForm(request.POST, instance=user_obj)

        if form.is_valid():
            obj = form.save(commit=False)

            password = form.cleaned_data.get('password')
            if password:
                obj.set_password(password)

            obj.save()

            role = form.cleaned_data.get('role')
            if role and role in dict(UserRole.ROLE_CHOICES):
                # Admin rolü sadece admin tarafından atanabilir
                if role == 'admin' and get_user_role(request.user) != 'admin':
                    messages.warning(request, "Only admins can create admin users.")
                    return redirect('user:user_permission_dashboard')
                
                UserRole.objects.update_or_create(user=obj, defaults={'role': role})

            messages.success(
                request,
                "User updated successfully." if user_obj else "User created successfully."
            )
            return redirect('user:user_permission_dashboard')

        users = User.objects.all().order_by("id")
        return render(request, 'user_permission_dashboard.html', {
            'users': users,
            'create_user_form': form
        })

    return redirect('user:user_permission_dashboard')


@admin_only
def user_permission_dashboard(request):
    users = User.objects.all().order_by("id")
    form = CreateUserForm()
    return render(request, 'user_permission_dashboard.html', {
        'users': users,
        'create_user_form': form
    })


@login_required
@admin_only
@require_POST
def delete_user(request, user_id):
    User = get_user_model()
    target = get_object_or_404(User, pk=user_id)

    # 1. Root kullanıcısı asla silinemez
    if target.username.lower() == 'root' or target.id == 1:
        messages.warning(request, "Root user cannot be deleted.")
        return redirect('user:user_permission_dashboard')

    # 2. Kullanıcı kendi hesabını silemez
    if target.id == request.user.id:
        messages.warning(request, "You cannot delete your own account.")
        return redirect('user:user_permission_dashboard')

    # 3. Admin kullanıcıları sadece admin silebilir
    # (Zaten @admin_only decorator var, bu kontrol ekstra güvenlik için)
    target_role = get_user_role(target)
    current_user_role = get_user_role(request.user)
    
    if target_role == "admin" and current_user_role != "admin":
        messages.warning(request, "Only admins can delete admin users.")
        return redirect('user:user_permission_dashboard')

    # Kullanıcıyı sil
    username = target.username
    target.delete()
    messages.success(request, f"User '{username}' deleted successfully.")
    return redirect('user:user_permission_dashboard')