from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction 
from django.core.paginator import Paginator
from datetime import timedelta, datetime, date

from .models import Benefit
from .forms import BenefitForm, BenefitBulkForm

@login_required
def benefit_list(request):
    q = request.GET.get('q')
    period = request.GET.get('period')
    qs = Benefit.objects.select_related('worker', 'worker__group', 'worker__s_no').all()

    if q:
        # sicil_no veya isimden arasın 
        qs = qs.filter(worker__sicil_no__icontains=q) | qs.filter(worker__name_surname__icontains=q)

        

    if period:
        try:
            start = datetime.strptime(period, "%Y-%m").date()
            end_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)  # sonraki ayın 1'i
            qs = qs.filter(period__gte=start, period__lt=end_month)
        except ValueError:
            pass  # yanlış tarih formatı varsa ignore et

    qs = qs.order_by('worker__sicil_no')
    paginator = Paginator(qs, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'benefits/benefit_list.html', {
        'page_obj': page_obj,
        'query': q or '',
        'selected_period': period or '',
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
            form.add_error('period', 'This worker already has a benefit record for this month.')
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
            form.add_error('worker', 'There is already a benefit record for this employee.')
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
                period = date(year, m, 1)
                if overwrite:
                    # Upsert: varsa güncelle, yoksa oluştur
                    obj, created = Benefit.objects.update_or_create(
                        worker=worker,
                        period=period,
                        defaults=defaults_common
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                else:
                    # overwrite kapalı ise: yoksa oluştur, varsa es geç
                    obj_exists = Benefit.objects.filter(worker=worker, period=period).exists()
                    if not obj_exists:
                        Benefit.objects.create(worker=worker, period=period, **defaults_common)
                        created_count += 1

        messages.success(
            request,
            f"İşlem tamamlandı: {created_count} yeni kayıt, {updated_count} güncelleme."
        )
        return redirect("benefits:list")

    return render(request, "benefits/benefit_bulk_form.html", {"form": form, "title": "Bulk Add/Update Benefits"})