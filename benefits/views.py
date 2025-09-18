from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.core.paginator import Paginator

from .models import Benefit
from .forms import BenefitForm

@login_required
def benefit_list(request):
    q = request.GET.get('q')
    qs = Benefit.objects.select_related('worker', 'worker__group', 'worker__s_no').all()

    if q:
        # sicil_no veya isimden arasın 
        qs = qs.filter(worker__sicil_no__icontains=q) | qs.filter(worker__name_surname__icontains=q)

    qs = qs.order_by('worker__sicil_no')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'benefits/benefit_list.html', {
        'page_obj': page_obj,
        'query': q or '',
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
            form.add_error('worker', 'There is already a benefit record for this employee.')
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
