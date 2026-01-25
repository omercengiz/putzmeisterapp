from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db import IntegrityError, transaction 
from django.core.paginator import Paginator
from datetime import timedelta, datetime, date
from decimal import Decimal, InvalidOperation
from .models import Benefit
from workers.models import Workers
from .forms import BenefitForm, BenefitBulkForm, BenefitImportForm
import pandas as pd
import datetime
import math

def parse_tr_decimal(value):
    """
    Türk Lirası formatını parse eder:
    10.000,32 -> 10000.32
    1.250 -> 1250
    boş / NaN -> 0
    """
    if value is None:
        return Decimal("0")

    # pandas NaN
    if isinstance(value, float) and math.isnan(value):
        return Decimal("0")

    try:
        s = str(value).strip()

        # Binlik ayırıcıyı kaldır
        s = s.replace(".", "")

        # Ondalık ayırıcıyı noktaya çevir
        s = s.replace(",", ".")

        return Decimal(s)
    except (InvalidOperation, ValueError):
        return Decimal("0")



@login_required
def benefit_list(request):
    q = request.GET.get('q')
    year = request.GET.get('year')
    month = request.GET.get('month')

    qs = Benefit.objects.select_related("worker", "worker__group", "worker__s_no").all()

    # Search filters
    if q:
        qs = qs.filter(
            worker__sicil_no__icontains=q
        ) | qs.filter(
            worker__name_surname__icontains=q
        )

    if year:
        qs = qs.filter(year=year)

    if month:
        qs = qs.filter(month=month)

    qs = qs.order_by('worker__sicil_no')

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    year_list = list(range(2020, datetime.date.today().year + 3))
    month_list = [
        (1, "January"), (2, "February"), (3, "March"),
        (4, "April"), (5, "May"), (6, "June"),
        (7, "July"), (8, "August"), (9, "September"),
        (10, "October"), (11, "November"), (12, "December"),
    ]

    month_dict = {
        1: "January", 2: "February", 3: "March",
        4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September",
        10: "October", 11: "November", 12: "December",
    }


    return render(request, 'benefits/benefit_list.html', {
        "page_obj": page_obj,
        "query": q or "",
        "selected_year": year or "",
        "selected_month": month or "",
        "year_list": year_list,
        "month_list": month_list,
        "month_dict": month_dict, 
    })


@login_required
def benefit_create(request):
    form = BenefitForm(request.POST or None)
    if form.is_valid():
        try:
            form.save()
            messages.success(request, "Benefits created successfully.")
            return redirect('benefits:list')
        except IntegrityError:
            # OneToOne 
            form.add_error('month', 'This worker already has a benefit record for this year/month.')
    return render(request, 'benefits/benefit_form.html', {'form': form, 'title': 'New Benefit'})

@login_required
def benefit_update(request, pk):
    benefit = get_object_or_404(Benefit, pk=pk)
    form = BenefitForm(request.POST or None, instance=benefit)
    if form.is_valid():
        try:
            form.save()
            messages.success(request, "Information of Benefits updated successfully.")
            return redirect('benefits:list')
        except IntegrityError:
            form.add_error('month', 'There is already a benefit record for this employee for that year/month.')
    return render(request, 'benefits/benefit_form.html', {'form': form, 'title': 'Update Benefit'})

@login_required
def benefit_delete(request, pk):
    benefit = get_object_or_404(Benefit, pk=pk)
    benefit.delete()
    messages.success(request, "Benefits deleted successfully.")
    return redirect('benefits:list')

@login_required
def benefit_bulk(request):
    form = BenefitBulkForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        short_class_action = request.POST.get("short_class_action")   # W / B / I veya None
        year   = form.cleaned_data["year"]
        months = form.cleaned_data["months"]
        overwrite = form.cleaned_data["overwrite_existing"]

        defaults_common = {
            "aile_yakacak": form.cleaned_data["aile_yakacak"],
            "erzak":         form.cleaned_data["erzak"],
            "altin":         form.cleaned_data["altin"],
            "bayram":        form.cleaned_data["bayram"],
            "dogum_evlenme": form.cleaned_data["dogum_evlenme"],
            "fon":           form.cleaned_data["fon"],
            "harcirah":      form.cleaned_data["harcirah"],
            "yol_parasi":    form.cleaned_data["yol_parasi"],
            "prim":          form.cleaned_data["prim"],
        }

        if short_class_action in ["W", "B", "I"]:
            workers = Workers.objects.filter(short_class__name=short_class_action)

            created_count = 0
            updated_count = 0

            with transaction.atomic():
                for w in workers:
                    for m in months:
                        if overwrite:
                            obj, created = Benefit.objects.update_or_create(
                                worker=w,
                                year=year,
                                month=m,
                                defaults=defaults_common
                            )
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1

                        else:
                            if not Benefit.objects.filter(worker=w, year=year, month=m).exists():
                                Benefit.objects.create(
                                    worker=w,
                                    year=year,
                                    month=m,
                                    **defaults_common
                                )
                                created_count += 1

            messages.success(
                request,
                f"{short_class_action} grubundaki çalışanlar için işlem tamamlandı → "
                f"{created_count} yeni kayıt, {updated_count} güncelleme."
            )
            return redirect("benefits:list")

        worker = form.cleaned_data["worker"]

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for m in months:
                if overwrite:
                    obj, created = Benefit.objects.update_or_create(
                        worker=worker,
                        year=year,
                        month=m,
                        defaults=defaults_common
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                else:
                    if not Benefit.objects.filter(worker=worker, year=year, month=m).exists():
                        Benefit.objects.create(
                            worker=worker,
                            year=year,
                            month=m,
                            **defaults_common
                        )
                        created_count += 1

        messages.success(
            request,
            f"İşlem tamamlandı: {created_count} yeni kayıt, {updated_count} güncelleme."
        )
        return redirect("benefits:list")

    return render(request, "benefits/benefit_bulk_form.html", {"form": form, "title": "Bulk Add/Update Benefits"})

    form = BenefitBulkForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        worker = form.cleaned_data["worker"]
        year   = form.cleaned_data["year"]
        months = form.cleaned_data["months"]
        overwrite = form.cleaned_data["overwrite_existing"]

        defaults_common = {
            "aile_yakacak": form.cleaned_data["aile_yakacak"],
            "erzak":         form.cleaned_data["erzak"],
            "altin":         form.cleaned_data["altin"],
            "bayram":        form.cleaned_data["bayram"],
            "dogum_evlenme": form.cleaned_data["dogum_evlenme"],
            "fon":           form.cleaned_data["fon"],
            "harcirah":      form.cleaned_data["harcirah"],
            "yol_parasi":    form.cleaned_data["yol_parasi"],
            "prim":          form.cleaned_data["prim"],
        }

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for m in months:
                if overwrite:
                    obj, created = Benefit.objects.update_or_create(
                        worker=worker,
                        year=year,
                        month=m,
                        defaults=defaults_common
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                else:
                    if not Benefit.objects.filter(worker=worker, year=year, month=m).exists():
                        Benefit.objects.create(worker=worker, year=year, month=m, **defaults_common)
                        created_count += 1

        messages.success(
            request,
            f"İşlem tamamlandı: {created_count} yeni kayıt, {updated_count} güncelleme."
        )
        return redirect("benefits:list")

    return render(request, "benefits/benefit_bulk_form.html", {"form": form, "title": "Bulk Add/Update Benefits"})

@login_required
def import_benefits(request):
    if request.method == "POST":
        form = BenefitImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            try:
                df = pd.read_excel(excel_file)

                
                required_columns = [
                    "sicil_no", "year", "month",
                    "aile_yakacak", "erzak", "altin",
                    "bayram", "dogum_evlenme", "fon",
                    "harcirah", "yol_parasi", "prim"
                ]
                missing = [c for c in required_columns if c not in df.columns]
                
                if missing:
                    messages.error(request, f"Missing columns: {', '.join(missing)}")
                    return redirect("benefits:import_benefits")

                for _, row in df.iterrows():
                    worker = Workers.objects.filter(sicil_no=row["sicil_no"]).first()
                    if not worker:
                        # Eşleşmeyen sicil_no → atla
                        continue

                    try:
                        year = int(row["year"])
                        month = int(row["month"])
                    except (ValueError, TypeError):
                        # Year/month okunamazsa o satırı atla
                        continue

                    Benefit.objects.update_or_create(
                        worker=worker,
                        year=year,
                        month=month,
                        defaults={
                            "aile_yakacak": parse_tr_decimal(row.get("aile_yakacak", 0)),
                            "erzak": parse_tr_decimal(row.get("erzak", 0)),
                            "altin": parse_tr_decimal(row.get("altin", 0)),
                            "bayram": parse_tr_decimal(row.get("bayram", 0)),
                            "dogum_evlenme": parse_tr_decimal(row.get("dogum_evlenme", 0)),
                            "fon": parse_tr_decimal(row.get("fon", 0)),
                            "harcirah": parse_tr_decimal(row.get("harcirah", 0)),
                            "yol_parasi": parse_tr_decimal(row.get("yol_parasi", 0)),
                            "prim": parse_tr_decimal(row.get("prim", 0)),
                        }
                    )

                messages.success(request, "Excel import has been successfully completed. ✅")
                return redirect('benefits:list')

            except Exception as e:
                messages.error(request, f"Import Error: {str(e)}")
                return redirect("benefits:import_benefits")
    else:
        form = BenefitImportForm()

    return render(request, "benefits/import_benefits.html", {"form": form})


@login_required
def download_benefit_template(request):
    columns = [
        "sicil_no",
        "year",
        "month",
        "aile_yakacak",
        "erzak",
        "altin",
        "bayram",
        "dogum_evlenme",
        "fon",
        "harcirah",
        "yol_parasi",
        "prim",
    ]

    # Kullanıcıya örnek olması için 1 satır
    data = [{
        "sicil_no": "123456",
        "year": 2025,
        "month": 1,
        "aile_yakacak": 0,
        "erzak": 0,
        "altin": 0,
        "bayram": 0,
        "dogum_evlenme": 0,
        "fon": 0,
        "harcirah": 0,
        "yol_parasi": 0,
        "prim": 0,
    }]

    df = pd.DataFrame(data, columns=columns)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        'attachment; filename="benefit_import_template.xlsx"'
    )

    df.to_excel(response, index=False)
    return response

