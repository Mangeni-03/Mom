from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.urls import reverse
from .forms import (
    MotherPregnancyForm, PregnancyNextVisitForm, VaccinationForm,
    ChildVaccinationForm, ChildForm
)
from .models import Mother, ChildVaccination, Pregnancy, Vaccination, Child
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


# ----------------------------
# Public Views
# ----------------------------

def landing(request):
    if request.user.is_authenticated:
        return redirect('staff_dashboard')
    return redirect('staff_login')


def register_mother(request):
    if request.method == 'POST':
        form = MotherPregnancyForm(request.POST)
        if form.is_valid():
            mother = form.save()
            return redirect('motherPage', pk=mother.id)
    else:
        form = MotherPregnancyForm()

    return render(request, 'Mom/register.html', {'form': form})


# ----------------------------
# Staff Views
# ----------------------------

@login_required
def staff_dashboard(request):
    mothers = Mother.objects.all().order_by('-created_at')
    return render(request, 'Mom/staff_dashboard.html', {'mothers': mothers})


@login_required
def staff_logout(request):
    logout(request)
    return redirect('staff_login')


@login_required
def motherPage(request, pk):
    mother = get_object_or_404(Mother, id=pk)
    today = timezone.now().date()

    # Automatically mark pregnancies as delivered if due date reached
    for p in mother.pregnancies.all():
        if p.due_date and p.due_date <= today:
            p.due_date = None  
            p.save()

    upcoming_vaccinations = ChildVaccination.objects.filter(
        child__mother=mother, completed=False
    ).order_by('scheduled_date')

    return render(request, 'Mom/mother.html', {
        'mother': mother,
        'upcoming_vaccinations': upcoming_vaccinations
    })


@login_required
def update_next_visit(request, pregnancy_id):
    pregnancy = get_object_or_404(Pregnancy, id=pregnancy_id)

    if request.method == 'POST':
        form = PregnancyNextVisitForm(request.POST, instance=pregnancy)
        if form.is_valid():
            form.save()
            return redirect('motherPage', pk=pregnancy.mother.id)
    else:
        form = PregnancyNextVisitForm(instance=pregnancy)

    return render(request, 'Mom/update_next_visit.html', {'form': form, 'pregnancy': pregnancy})


# ----------------------------
# Vaccination Views
# ----------------------------

@login_required
def vaccination_list(request):
    vaccinations = Vaccination.objects.all().order_by('dose_order')
    return render(request, 'Mom/vaccination_list.html', {'vaccinations': vaccinations})


@login_required
def vaccination_create(request):
    if request.method == 'POST':
        form = VaccinationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vaccination_list')
    else:
        form = VaccinationForm()

    return render(request, 'Mom/form.html', {'form': form, 'title': 'Add Vaccination'})


# ----------------------------
# Schedule Vaccination for a Child
# ----------------------------

@login_required
def schedule_child_vaccination(request, pk):
    child = get_object_or_404(Child, id=pk)

    if request.method == 'POST':
        form = ChildVaccinationForm(request.POST)
        if form.is_valid():
            child_vaccination = form.save(commit=False)
            child_vaccination.child = child
            child_vaccination.save()

            return redirect('child_detail', pk=child.id)

    else:
        form = ChildVaccinationForm()

    return render(request, 'Mom/child_vaccination_form.html', {
        'form': form,
        'child': child
    })

@login_required
def complete_vaccination(request, pk):
    vaccination = get_object_or_404(ChildVaccination, id=pk)
    vaccination.completed = True
    vaccination.save()
    return redirect('child_detail', pk=vaccination.child.id)

# ----------------------------
# Child Views
# ----------------------------

def child_list(request):
    children = Child.objects.all().order_by('name')
    return render(request, 'Mom/child.html', {'children': children})


# Add new child normally (NOT linked to mother)
def add_child(request):
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('child_list')
    else:
        form = ChildForm()

    return render(request, 'Mom/child_form.html', {'form': form})


# Add child UNDER a specific mother
@login_required
def add_child_to_mother(request, mother_id):
    mother = get_object_or_404(Mother, id=mother_id)

    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.mother = mother
            child.save()
            return redirect('motherPage', pk=mother.id)

    else:
        form = ChildForm()

    return render(request, 'Mom/child_form.html', {
        'form': form,
        'mother': mother
    })


# ----------------------------
# Child Detail Page
# ----------------------------

def child_detail(request, pk):
    child = get_object_or_404(Child, id=pk)
    upcoming_vaccinations = child.vaccinations.filter(completed=False).order_by('scheduled_date')

    return render(request, 'Mom/child_detail.html', {
        'child': child,
        'upcoming_vaccinations': upcoming_vaccinations
    })


    