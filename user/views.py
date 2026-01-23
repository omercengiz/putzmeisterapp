from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm, CreateUserForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import UserRole


# Create your views here.
def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")

        newUser = User(username=username)
        newUser.set_password(password) # encrypted
        newUser.save()
        login(request, newUser)
        messages.success(request, "You registered, successfully...")
        return redirect("index")
        
    context = {
        "form": form
    }
    return render(request, "register.html", context)


def loginUser(request):
    form = LoginForm(request.POST or None)
    context = {
        "form": form
    }
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        
        if user is None:
            messages.info(request,"Username or password is wrong...")
            return render(request, "login.html", context)

        messages.success(request, "You logged in successfully...")
        login(request, user)
        return redirect("index")
    return render(request, "login.html", context)


def logoutUser(request):
    logout(request)
    #messages.success(request, "You logged out successfully...")
    return redirect("user:login")


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('user:login')  
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if not hasattr(request.user, 'role_info'):
            return render(request, '403.html', status=403)
        if request.user.role_info.role != 'admin':
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def update_user_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in dict(UserRole.ROLE_CHOICES):
            UserRole.objects.update_or_create(user=user, defaults={'role': role})
    return redirect('user:user_permission_dashboard')


@admin_required
def create_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_obj = get_object_or_404(User, pk=user_id) if user_id else None

        form = CreateUserForm(request.POST, instance=user_obj)

        if form.is_valid():
            obj = form.save(commit=False)

            password = form.cleaned_data.get('password')
            if password:
                obj.set_password(password)  # ✔ sadece doluysa

            obj.save()

            role = form.cleaned_data.get('role')
            if role and role in dict(UserRole.ROLE_CHOICES):
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




@admin_required
def user_permission_dashboard(request):
    users = User.objects.all().order_by("id")
    form = CreateUserForm()
    return render(request, 'user_permission_dashboard.html', {
        'users': users,
        'create_user_form': form
    })



@login_required
@admin_required
@require_POST
def delete_user(request, user_id):
    User = get_user_model()
    target = get_object_or_404(User, pk=user_id)

    # Kendini silme koruması yarattık bu önemli 
    if target.id == request.user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user:user_permission_dashboard')

    # Süper kullanıcıyı ancak süper kullanıcı silebilsin (opsiyonel ama iyi pratik)
    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Admin users can only be deleted by other admins.")
        return redirect('user:user_permission_dashboard')

    # Sil ve rol kaydını otomatik cascadeliyorsa ekstra işleme gerek yok
    target.delete()
    messages.success(request, f"'{target.username}' user deleted successfully.")
    return redirect('user:user_permission_dashboard')