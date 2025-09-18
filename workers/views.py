from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .forms import WorkersForm
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Workers, ArchivedWorker
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .lookups import Group, ShortClass, DirectorName, Currency, WorkClass, ClassName, Department, CostCenter
from django.forms import modelform_factory
from django.views.decorators.http import require_POST
from django.apps import apps

lookup_models = {
    "Group": Group,
    "ShortClass": ShortClass,
    "DirectorName": DirectorName,
    "Currency": Currency,
    "WorkClass": WorkClass,
    "ClassName": ClassName,
    "Department": Department,
    "CostCenter": CostCenter,
}


def is_sicil_no_exist(sicil_no: str) -> bool:
    return (
        Workers.objects.filter(sicil_no=sicil_no).exists()
        or ArchivedWorker.objects.filter(sicil_no=sicil_no).exists()
    )

# Create your views here.
@login_required
def index(request):
    return render(request, "index.html")

@login_required(login_url="user:login")
def detail(request, id):
    return HttpResponse("Detail:" + str(id))

@login_required(login_url="user:login")
def dashboard(request):
    query = request.GET.get("q")
    if query:
        workers = Workers.objects.filter(sicil_no__iexact=query)
    else:
        workers = Workers.objects.all()
    
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
        sicil = worker.sicil_no

        if is_sicil_no_exist(sicil):
            form.add_error("sicil_no", "This Sicil No already exists in the system.")
        else:
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
        new_sicil = updated_worker.sicil_no

        exists_workers = Workers.objects.exclude(id=worker.id).filter(sicil_no=new_sicil).exists()
        exits_archived = ArchivedWorker.objects.filter(sicil_no=new_sicil).exists()

        # Aynı sicil_no başka bir kayıtla çakışıyor mu kontrolü
        if exists_workers or exits_archived:
            form.add_error("sicil_no", "This Sicil No is already used by another worker.")
        else:
            updated_worker.save()
            messages.success(request, "Information of the worker has been updated successfully.")
            return redirect("workers:dashboard")
        
    return render(request, "updateworkers.html", {"form": form})


@login_required(login_url="user:login")
@require_POST
def deleteWorkers(request, id):
    worker = get_object_or_404(Workers, id=id)

    # Modal formundan gelen çıkış tarihi (YYYY-MM-DD)
    exit_date = request.POST.get('exit_date')

    # Arşive eklerken çıkış tarihini de yaz
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
        bonus=worker.bonus,
        # 👇 ArchivedWorker modelinde bu alanın adı neyse onu kullan:
        exit_date=exit_date  # ör: 'exit_date' / 'terminated_at'
    )

    worker.delete()
    messages.success(request, "Worker deleted and archived.")
    return redirect("workers:dashboard")


def manage_lookups(request):
    forms_and_items = []

    for name, model in lookup_models.items():
        form_class = modelform_factory(model, fields="__all__")
        form = form_class(prefix=name)
        items = model.objects.all()
        forms_and_items.append({
            "name": name,
            "form": form,
            "items": items,
            "model_name": model.__name__
        })

    if request.method == "POST":
        form_name = request.POST.get("form_name")
        model = lookup_models.get(form_name)
        form_class = modelform_factory(model, fields="__all__")
        form = form_class(request.POST, prefix=form_name)
        if form.is_valid():
            form.save()
            return redirect("manage_lookups")

    return render(request, "lookups/manage_lookups.html", {
        "forms_and_items": forms_and_items,
    })

def delete_lookup(request, model_name, pk):
    model = lookup_models.get(model_name)
    if not model:
        return redirect("manage_lookups")

    obj = get_object_or_404(model, pk=pk)
    obj.delete()
    return redirect("manage_lookups")


def update_lookup(request, model_name, pk):
    Model = apps.get_model(app_label='workers', model_name=model_name)
    obj = get_object_or_404(Model, pk=pk)

    if request.method == 'POST':
        for field, value in request.POST.items():
            if field.endswith('-csrfmiddlewaretoken') or field == 'csrfmiddlewaretoken':
                continue
            # Örn: 'CostCenter-code' veya 'Department-name'
            if '-' in field:
                _, real_field = field.split('-', 1)
                if hasattr(obj, real_field):
                    setattr(obj, real_field, value)
        obj.save()
        return redirect('manage_lookups')  # burası önemli

    # GET istekleri için de redirect et
    return redirect('manage_lookups')
