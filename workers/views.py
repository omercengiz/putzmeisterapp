from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .forms import WorkersForm, GrossSalaryBulkForm, WorkerGrossMonthlyForm, WorkerImportForm
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Workers, ArchivedWorker, WorkerGrossMonthly, ArchivedWorkerGrossMonthly
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .lookups import Group, ShortClass, DirectorName, Currency, WorkClass, ClassName, Department, CostCenter, ExitReason
from django.forms import modelform_factory
from django.views.decorators.http import require_POST
from django.apps import apps
import calendar
import datetime
import pandas as pd
from benefits.models import Benefit, ArchivedBenefit




lookup_models = {
    "Group": Group,
    "ShortClass": ShortClass,
    "DirectorName": DirectorName,
    "Currency": Currency,
    "WorkClass": WorkClass,
    "ClassName": ClassName,
    "Department": Department,
    "CostCenter": CostCenter,
    "ExitReason": ExitReason,
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
    workers = Workers.objects.all()

    # Arama
    if query:
        workers = workers.filter(
            sicil_no__icontains=query
        ) | workers.filter(
            name_surname__icontains=query
        )

    # Sayfalama
    paginator = Paginator(workers, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "dashboard.html",
        {
            "page_obj": page_obj,
            "query": query,
            "exit_reasons": ExitReason.objects.all(),  
        }
    )



@login_required(login_url="user:login")
def AddWorkers(request):
    form = WorkersForm(request.POST or None)
    
    if form.is_valid():
        worker = form.save(commit=False)
        worker.author = request.user
        sicil = worker.sicil_no
        worker.update_date_user = datetime.date.today()

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

        #if sicil_no exists then check(overlap)
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

    #if sicil_no startwith("P"): then deletion but no archive
    if worker.sicil_no and worker.sicil_no.startswith("P"):
        worker.delete()
        messages.warning(
            request,
            f"The record was deleted without being archived or asking for the exit date because the Sicil No {worker.sicil_no} starts with 'P'."
        )
        return redirect("workers:dashboard")

    exit_date = request.POST.get('exit_date')
    exit_reason_id = request.POST.get("exit_reason")
    exit_reason = ExitReason.objects.filter(id=exit_reason_id).first()

    archived_worker = ArchivedWorker.objects.filter(sicil_no=worker.sicil_no).first()

    # ArchivedWorker creation
    if archived_worker is None:
        # İlk kez arşivleniyor
        archived_worker = ArchivedWorker.objects.create(
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
            exit_date=exit_date,
            exit_reason=exit_reason
        )
    else:
        # Daha önce arşivlenmiş olabilir → son bilgileri güncelle
        archived_worker.group = worker.group
        archived_worker.s_no = worker.s_no
        archived_worker.department_short_name = worker.department_short_name
        archived_worker.department = worker.department
        archived_worker.short_class = worker.short_class
        archived_worker.name_surname = worker.name_surname
        archived_worker.date_of_recruitment = worker.date_of_recruitment
        archived_worker.work_class = worker.work_class
        archived_worker.class_name = worker.class_name
        archived_worker.gross_payment = worker.gross_payment
        archived_worker.currency = worker.currency
        archived_worker.bonus = worker.bonus
        archived_worker.exit_date = exit_date
        archived_worker.exit_reason = exit_reason
        archived_worker.save()


    # Worker’a ait Benefit kayıtlarını arşivle
    benefits = Benefit.objects.filter(worker=worker)
    archived_benefits = []
    for b in benefits:
        archived_benefits.append(ArchivedBenefit(
            archived_worker=archived_worker,
            sicil_no=worker.sicil_no,
            period=b.period,
            aile_yakacak=b.aile_yakacak,
            erzak=b.erzak,
            altin=b.altin,
            bayram=b.bayram,
            dogum_evlenme=b.dogum_evlenme,
            fon=b.fon,
            harcirah=b.harcirah,
            yol_parasi=b.yol_parasi,
            prim=b.prim
        ))

    if archived_benefits:
        ArchivedBenefit.objects.bulk_create(archived_benefits)

    # Orijinal benefit kayıtlarını sil
    benefits.delete()

    # Worker’a ait maaş kayıtlarını al
    salaries = WorkerGrossMonthly.objects.filter(worker=worker)
    archived_salaries = []

    for s in salaries:
        archived_salaries.append(ArchivedWorkerGrossMonthly(
            archived_worker=archived_worker,
            year=s.year,
            month=s.month,
            gross_salary=s.gross_salary,
            currency=s.currency,
            sicil_no=s.sicil_no,
            created_at=s.created_at,
            updated_at=s.updated_at,
        ))

    if archived_salaries:
        ArchivedWorkerGrossMonthly.objects.bulk_create(archived_salaries)

    # Orijinal maaş kayıtlarını sil
    salaries.delete()

    # Worker kaydını sil
    worker.delete()

    messages.success(
        request,
        f"Sicil No:{worker.sicil_no} - {worker.name_surname} deleted and archived (including benefits & all salaries)."
    )
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
        return redirect('manage_lookups')  

    return redirect('manage_lookups')


def bulk_set_gross_salaries(request):
    if request.method == "POST":
        form = GrossSalaryBulkForm(request.POST)
        # refresh=1 ise sadece formu yeniden göster (auto-prefill yapıldı)
        if request.POST.get('refresh') == '1':
            return render(request, "bulk_gross_salaries.html", {"form": form})

        if form.is_valid():
            worker = form.cleaned_data['worker']
            year = form.cleaned_data['year']
            months = form.cleaned_data['months']
            gross_salary = form.cleaned_data['gross_salary']
            overwrite = form.cleaned_data['overwrite_existing']

            for m in months:
                if overwrite:
                    WorkerGrossMonthly.objects.update_or_create(
                        worker=worker, year=year, month=m,
                        defaults={'gross_salary': gross_salary, 'currency': worker.currency},
                    )
                else:
                    WorkerGrossMonthly.objects.get_or_create(
                        worker=worker, year=year, month=m,
                        defaults={'gross_salary': gross_salary, 'currency': worker.currency},
                    )

            messages.success(request, f"{worker.sicil_no} ({worker.name_surname}) için kayıtlar güncellendi.")
            return redirect("workers:list_worker_salaries", worker_id=worker.id)
    else:
        form = GrossSalaryBulkForm()

    return render(request, "bulk_gross_salaries.html", {"form": form})



@login_required
def update_salary_record(request, salary_id):

    # Yeni kayıt mı kontrolü
    is_new_record = (salary_id == 0)

    # -----------------------------
    # 1. GET – Formu sadece göster
    # -----------------------------
    if request.method == "GET":
        if is_new_record:
            worker_id = request.GET.get("worker_id")
            #month = int(request.GET.get("month"))
            #year = int(request.GET.get("year"))
            # Yıl bazen "2.025" gibi gelebiliyor → sadece rakamları al
            raw_year = request.GET.get("year", "")
            year = int("".join(filter(str.isdigit, raw_year))) if raw_year else datetime.date.today().year

            # Ay: bazen "1.0" gibi gelebiliyor → float → int
            raw_month = request.GET.get("month", "")
            month = int(float(raw_month)) if raw_month else datetime.date.today().month

            worker = get_object_or_404(Workers, id=worker_id)

            # GET aşamasında kesinlikle kayıt oluşturulmuyor!
            salary = WorkerGrossMonthly(
                worker=worker,
                year=year,
                month=month,
                gross_salary=worker.gross_payment or 0,
                currency=worker.currency,
            )
        else:
            salary = get_object_or_404(WorkerGrossMonthly, id=salary_id)
            worker = salary.worker

        form = WorkerGrossMonthlyForm(instance=salary)
        form.fields["currency"].disabled = True

        return render(request, "update_salary.html", {
            "form": form,
            "salary": salary,
            "worker": worker,
        })

    # -----------------------------
    # 2. POST – Save işlemi
    # -----------------------------
    if request.method == "POST":

        if is_new_record:
            worker_id = request.GET.get("worker_id")
            #month = int(request.GET.get("month"))
            #year = int(request.GET.get("year"))

            raw_year = request.GET.get("year", "")
            year = int("".join(filter(str.isdigit, raw_year))) if raw_year else datetime.date.today().year

            # Ay: bazen "1.0" gibi gelebiliyor → float → int
            raw_month = request.GET.get("month", "")
            month = int(float(raw_month)) if raw_month else datetime.date.today().month

            worker = get_object_or_404(Workers, id=worker_id)

            # şimdi create edilebilir
            salary, _ = WorkerGrossMonthly.objects.get_or_create(
                worker=worker,
                year=year,
                month=month,
                defaults={
                    "gross_salary": worker.gross_payment or 0,
                    "currency": worker.currency,
                    "sicil_no": worker.sicil_no
                }
            )
        else:
            salary = get_object_or_404(WorkerGrossMonthly, id=salary_id)
            worker = salary.worker

        form = WorkerGrossMonthlyForm(request.POST, instance=salary)
        form.fields["currency"].disabled = True

        if form.is_valid():
            updated = form.save(commit=False)
            updated.currency = worker.currency
            updated.sicil_no = worker.sicil_no  # güvenlik
            updated.save()

            messages.success(request, "Salary record saved successfully.")
            return redirect("workers:list_worker_salaries", worker_id=worker.id)

        # Form geçersizse tekrar yüklenir
        return render(request, "update_salary.html", {
            "form": form,
            "salary": salary,
            "worker": worker,
        })


def list_worker_salaries(request, worker_id):
    worker = get_object_or_404(Workers, id=worker_id)

    # YIL FİLTRESİ
    selected_year = request.GET.get("year")
    current_year = datetime.date.today().year

    try:
        selected_year = int(selected_year) if selected_year else current_year
    except:
        selected_year = current_year

    # Dropdownda göstermek için
    year_list = list(range(2015, current_year + 1))

    salaries = WorkerGrossMonthly.objects.filter(worker=worker, year=selected_year)
    salaries_dict = {s.month: s for s in salaries}

    months_data = []
    for m in range(1, 13):
        months_data.append({
            "month": calendar.month_name[m],
            "month_num": m,
            "year": selected_year,
            "salary": salaries_dict.get(m),
        })

    return render(request, "worker_salary_list.html", {
        "worker": worker,
        "months_data": months_data,
        "year_list": year_list,
        "selected_year": selected_year,
    })

def delete_salary_record(request, salary_id):
    salary = get_object_or_404(WorkerGrossMonthly, pk=salary_id)
    worker_id = salary.worker.id
    worker_name = salary.worker.name_surname
    salary.delete()
    messages.success(request, f"{worker_name} için maaş kaydı silindi.")
    return redirect("workers:list_worker_salaries", worker_id=worker_id)

@login_required
def import_workers(request):
    if request.method == "POST":
        form = WorkerImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data["excel_file"]

            try:
                df = pd.read_excel(excel_file)

                # column mapping
                column_mapping = {
                    "Group": "group",
                    "Sicil No": "sicil_no",
                    "CostCenter": "s_no",   
                    "Directorships": "department_short_name",
                    "Status": "short_class",
                    "Name surname": "name_surname",
                    "Date of recruitment": "date_of_recruitment",
                    "Work class": "work_class",
                    "Class name": "class_name",
                    "Department": "department",
                    "Gross payment": "gross_payment",
                    "Currency": "currency",
                    "Bonus": "bonus",
                }

                # normalize name of columns
                df.rename(columns=lambda c: c.strip(), inplace=True)
                df.rename(columns=column_mapping, inplace=True)

                required_columns = list(column_mapping.values())
                missing = [c for c in required_columns if c not in df.columns]
                if missing:
                    messages.error(
                        request,
                        f"❌ Excel dosyasında eksik kolon(lar) var → {', '.join(missing)}",
                        extra_tags="danger"
                    )
                    return redirect("workers:import_workers")

                # Lookup models
                lookups = {
                    "s_no": (CostCenter, "code"),
                    "group": (Group, "name"),
                    "short_class": (ShortClass, "name"),
                    "department_short_name": (DirectorName, "name"),
                    "currency": (Currency, "code"),
                    "work_class": (WorkClass, "name"),
                    "class_name": (ClassName, "name"),
                    "department": (Department, "name"),
                }

                for index, row in df.iterrows():
                    sicil_no = str(row["sicil_no"]).strip()

                    # ✅ Date Check
                    date_val = row.get("date_of_recruitment")
                    if pd.isna(date_val) or date_val == "":
                        messages.error(
                            request,
                            f"❌ {index+2}. satır (Sicil No: {sicil_no}) → 'date_of_recruitment' boş olamaz.",
                            extra_tags="danger"
                        )
                        return redirect("workers:import_workers")

                    if isinstance(date_val, str):
                        try:
                            date_val = datetime.datetime.strptime(date_val, "%Y-%m-%d")
                        except ValueError:
                            messages.error(
                                request,
                                f"❌ {index+2}. satır (Sicil No: {sicil_no}) → 'date_of_recruitment' formatı hatalı. "
                                f"Beklenen format: YYYY-MM-DD (örnek: 2025-01-15).",
                                extra_tags="danger"
                            )
                            return redirect("workers:import_workers")

                    # ✅ Lookup confirm
                    lookup_ids = {}
                    for col, (Model, field) in lookups.items():
                        val = row.get(col)
                        if pd.isna(val) or val == "":
                            messages.error(
                                request,
                                f"❌ {index+2}. satır (Sicil No: {sicil_no}) → '{col}' boş olamaz.",
                                extra_tags="danger"
                            )
                            return redirect("workers:import_workers")

                        obj = Model.objects.filter(**{field: val}).first()
                        if not obj:
                            messages.error(
                                request,
                                f"❌ {index+2}. satır (Sicil No: {sicil_no}) → '{col}' alanında girilen '{val}' "
                                f"lookup tablosunda yok.",
                                extra_tags="danger"
                            )
                            return redirect("workers:import_workers")

                        lookup_ids[f"{col}_id"] = obj.id

                    # ✅ Worker add/update
                    Workers.objects.update_or_create(
                        sicil_no=sicil_no,
                        defaults={
                            "name_surname": row.get("name_surname"),
                            "date_of_recruitment": date_val,
                            "gross_payment": row.get("gross_payment", 0),
                            "bonus": row.get("bonus", 0),
                            "author_id": request.user.id,
                            **lookup_ids
                        }
                    )

                messages.success(
                    request,
                    "✔️ Excel import işlemi başarıyla tamamlandı.",
                    extra_tags="success"
                )
                return redirect("workers:dashboard")

            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Import sırasında beklenmeyen hata: {str(e)}")

                messages.error(
                    request,
                    "⚠️ Beklenmeyen bir hata oluştu. Lütfen sistem yöneticisi ile iletişime geçin.",
                    extra_tags="danger"
                )
                return redirect("workers:import_workers")

    else:
        form = WorkerImportForm()

    return render(request, "import_workers.html", {"form": form})
