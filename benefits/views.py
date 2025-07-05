from django.shortcuts import render, redirect
from .forms import BenefitForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url="user:login")
def add_benefit(request):
    form = BenefitForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Benefit has been added successfully.")
        return redirect("benefits:add_benefit")
    
    return render(request, "benefits/add_benefit.html", {"form": form})
