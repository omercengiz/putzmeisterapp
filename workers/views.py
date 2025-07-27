from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .forms import WorkersForm
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Workers, ArchivedWorker
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError


# Create your views here.
def index(request):
    return render(request, "index.html")

@login_required(login_url="user:login")
def detail(request, id):
    return HttpResponse("Detail:" + str(id))

@login_required(login_url="user:login")
def dashboard(request):
    query = request.GET.get("q")
    if query:
        workers = Workers.objects.filter(author=request.user, sicil_no__iexact=query)
    else:
        workers = Workers.objects.filter(author=request.user)
    
    paginator = Paginator(workers, 5)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query
    }
    return render(request, "dashboard.html", context)


@login_required(login_url="user:login")
def AddWorkers(request):
    form = WorkersForm(request.POST or None)
    
    if form.is_valid():
        worker = form.save(commit=False)
        worker.author = request.user
        try:
            worker.save()
            messages.success(request, "Member has been added successfully...")
            return redirect("workers:dashboard")
        except IntegrityError:
            form.add_error("sicil_no", "This Sicil No already exists.")

    return render(request, "addworkers.html", {"form": form})



@login_required(login_url="user:login")
def updateWorkers(request, id):
    worker = get_object_or_404(Workers, id=id)
    form = WorkersForm(request.POST or None, instance=worker)
    
    if form.is_valid():
        updated_worker = form.save(commit=False)
        updated_worker.author = request.user

        # Aynı sicil_no başka bir kayıtla çakışıyor mu kontrolü
        if Workers.objects.exclude(id=worker.id).filter(sicil_no=updated_worker.sicil_no).exists():
            form.add_error("sicil_no", "This Sicil No is already used by another worker.")
        else:
            updated_worker.save()
            messages.success(request, "Information of the worker has been updated successfully.")
            return redirect("workers:dashboard")
        
    return render(request, "updateworkers.html", {"form": form})

@login_required(login_url="user:login")
def deleteWorkers(request, id):
    worker = get_object_or_404(Workers, id=id)

    ArchivedWorker.objects.create(
        original_id=worker.id,
        created_date=worker.created_date,
        author=worker.author,
        group=worker.group,
        sicil_no=worker.sicil_no,
        s_no=worker.s_no,
        department_short_name=worker.department_short_name,
        department=worker.department,
        short_class=worker.short_class,
        name_surname=worker.name_surname,
        date_of_recruitment=worker.date_of_recruitment,
        work_class=worker.work_class,
        class_name=worker.class_name,
        gross_payment=worker.gross_payment,
        currency=worker.currency,
        bonus=worker.bonus
    )

    worker.delete()
    messages.success(request, "Worker deleted and archived.")
    return redirect("workers:dashboard")