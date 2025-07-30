from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import UserRole
from .forms import CreateUserForm


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
    messages.success(request, "You logged out successfully...")
    return redirect("index")


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
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # şifreyi hashle
            user.save()

            # Role kaydını da oluştur
            role = form.cleaned_data['role']
            UserRole.objects.create(user=user, role=role)

            messages.success(request, f"Kullanıcı '{user.username}' başarıyla oluşturuldu.")
            return redirect('user:user_permission_dashboard')
    else:
        form = CreateUserForm()
    return render(request, 'user_create.html', {'form': form})


@admin_required
def user_permission_dashboard(request):
    users = User.objects.all()
    form = CreateUserForm()
    return render(request, 'user_permission_dashboard.html', {
        'users': users,
        'create_user_form': form
    })
