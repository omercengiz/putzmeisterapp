from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .forms import WorkersForm
from django.contrib import messages
from .models import Workers
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, "index.html")

@login_required(login_url="user:login")
def detail(request, id):
    return HttpResponse("Detail:" + str(id))

@login_required(login_url="user:login")
def dashboard(request):
    workers = Workers.objects.filter(author=request.user)
    context = {
        "workers":workers
    }
    return render(request, "dashboard.html", context)

@login_required(login_url="user:login")
def AddWorkers(request):
    form = WorkersForm(request.POST or None)
    
    if form.is_valid():
        worker = form.save(commit=False)
        worker.author = request.user
        worker.save()
        messages.success(request, "Member has been added successfully...")
        return redirect("workers:dashboard")
    return render(request, "addworkers.html", {"form":form})


@login_required(login_url="user:login")
def updateWorkers(request, id):
    worker = get_object_or_404(Workers, id=id)
    form = WorkersForm(request.POST or None, request.FILES or None, instance=worker)
    if form.is_valid():
        worker = form.save(commit=False)
        worker.author = request.user
        worker.save()
        messages.success(request, "Information of the worker has been updated, successfully...")
        return redirect("workers:dashboard")
    
    return render(request, "updateworkers.html", {"form":form})

@login_required(login_url="user:login")
def deleteWorkers(request, id):
    worker = get_object_or_404(Workers, id=id)
    worker.delete()
    messages.success(request, "Information of the worker has been deleted")

    return redirect("workers:dashboard")
