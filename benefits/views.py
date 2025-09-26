from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.core.paginator import Paginator
from datetime import timedelta, datetime

from .models import Benefit
from .forms import BenefitForm

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
    paginator = Paginator(qs, 5)
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
