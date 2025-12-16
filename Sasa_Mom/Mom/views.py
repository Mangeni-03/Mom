from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.urls import reverse
# NEW IMPORTS for Superuser Restriction
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout
# END NEW IMPORTS

from .forms import (
    MotherPregnancyForm, PregnancyNextVisitForm, VaccinationForm,
    ChildVaccinationForm, ChildForm, MotherForm,PregnancyForm
)
from .models import Mother, ChildVaccination, Pregnancy, Vaccination, Child

# ----------------------------
# Access Control Helper
# ----------------------------

def is_superuser_check(user):
    """Custom test function to check if the user is a superuser."""
    # Ensure user is logged in (active) and has superuser status
    return user.is_active and user.is_superuser


# ----------------------------
# Public Views
# ----------------------------

def landing(request):
    if request.user.is_authenticated:
        return redirect('staff_dashboard')
    return redirect('staff_login')


# Mom/views.py

def register_mother(request):
    if request.method == 'POST':
        form = MotherPregnancyForm(request.POST)
        if form.is_valid():
            mother = form.save()
            
            if mother.already_given_birth:
                # Redirect to the add_child view, linked to the new mother's ID
                return redirect('add_child_to_mother', mother_id=mother.id)
            
            # Otherwise, redirect to the mother's profile page
            return redirect('motherPage', pk=mother.id)
            
    else:
        form = MotherPregnancyForm()

    return render(request, 'Mom/register.html', {'form': form})

# RESTRICTED VIEW: Mother Editing
@user_passes_test(is_superuser_check)
def editMother(request, pk):
    """
    Handles the editing of a Mother's profile.
    ACCESS: Superuser only.
    """
    mother = get_object_or_404(Mother, id=pk)
    
    # Check if the request is a POST (form submission)
    if request.method == 'POST':
        # Populate the form with data from the request and the existing instance
        form = MotherForm(request.POST, instance=mother)
        if form.is_valid():
            form.save()
            # Assuming 'mother_profile' is the correct URL name for motherPage
            return redirect('motherPage', pk=mother.id) 
    else:
        # If it's a GET request, create the form instance with the existing data
        form = MotherForm(instance=mother)

    context = {'form': form, 'mother': mother}
    return render(request, 'Mom/edit_mother.html', context)

# ----------------------------
# Staff Views (Keep @login_required unless otherwise specified)
# ----------------------------

@login_required
def staff_dashboard(request):
    mothers = Mother.objects.all().order_by('-created_at')
    return render(request, 'Mom/staff_dashboard.html', {'mothers': mothers})


@login_required
def staff_logout(request):
    logout(request)
    return redirect('staff_login')


from django.db.models import Q

@login_required
def motherPage(request, pk):
    mother = get_object_or_404(Mother, id=pk)
    
    # 1. Filter out pregnancy records that are effectively empty (no due date)
    active_pregnancies = mother.pregnancies.filter(due_date__isnull=False).order_by('-due_date')

    # 2. Aggregate upcoming vaccinations for ALL children
    child_ids = mother.children.values_list('id', flat=True)
    upcoming_vaccinations = ChildVaccination.objects.filter(
        child__in=child_ids,
        completed=False,
        scheduled_date__gte=timezone.localdate()
    ).order_by('scheduled_date')

    context = {
        'mother': mother,
        'upcoming_vaccinations': upcoming_vaccinations,
        # Pass the filtered queryset to the template
        'pregnancies': active_pregnancies, 
    }
    return render(request, 'Mom/mother.html', context)

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


# RESTRICTED VIEW: Creating/Adding a new base vaccination type
@user_passes_test(is_superuser_check)
def vaccination_create(request):
    """
    Handles the creation of a new Vaccination type.
    ACCESS: Superuser only.
    """
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

@login_required
def child_list(request):
    children = Child.objects.all().order_by('name')
    return render(request, 'Mom/child.html', {'children': children})


# RESTRICTED VIEW: Adding a child without mother context (general registry entry)
@user_passes_test(is_superuser_check)
def add_child(request):
    """
    Handles adding a child without linking to a specific mother.
    ACCESS: Superuser only.
    """
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('child_list')
    else:
        form = ChildForm()

    return render(request, 'Mom/child_form.html', {'form': form})

# RESTRICTED VIEW: Child Editing
@user_passes_test(is_superuser_check)
def editChild(request, pk):
    """
    Handles the editing of a Child's profile details.
    ACCESS: Superuser only.
    """
    child = get_object_or_404(Child, id=pk)
    
    if request.method == 'POST':
        # Populate the form with data from the request and the existing instance
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            # Redirect back to the child's profile page after successful update
            return redirect('child_detail', pk=child.id) 
    else:
        # If it's a GET request, create the form instance with the existing data
        form = ChildForm(instance=child)

    context = {'form': form, 'child': child}
    return render(request, 'Mom/edit_child.html', context)

# Allow authenticated staff to add child to a mother's profile
# Mom/views.py

from .utils import schedule_initial_vaccinations # Ensure this is imported

@login_required
def add_child_to_mother(request, mother_id):
    mother = get_object_or_404(Mother, id=mother_id)

    if request.method == 'POST':
        form = ChildForm(request.POST) 
        if form.is_valid():
            child = form.save(commit=False)
            child.mother = mother
            child.save() 
            
            schedule_initial_vaccinations(child) 

            # Successful POST returns a redirect
            return redirect('motherPage', pk=mother.id)

    else:
        # GET request: Instantiate an empty form
        form = ChildForm()

    # Final Return: Renders the page for GET, or for an invalid POST
    return render(request, 'Mom/child_form.html', {
        'form': form,
        'mother': mother
    })
# ----------------------------
# Child Detail Page
# ----------------------------

# Mom/views.py

# ... (other views and imports)

# ----------------------------
# Child Detail Page
# ----------------------------

@login_required
def child_detail(request, pk):
    child = get_object_or_404(Child, id=pk)
    
    # FIX APPLIED: Using the correct related_name 'vaccinations'
    
    # Upcoming (Completed=False)
    upcoming_vaccinations = child.vaccinations.filter(completed=False).order_by('scheduled_date')
    
    # Completed (Completed=True)
    completed_vaccinations = child.vaccinations.filter(completed=True).order_by('-scheduled_date')

    return render(request, 'Mom/child_detail.html', {
        'child': child,
        'upcoming_vaccinations': upcoming_vaccinations,
        'completed_vaccinations': completed_vaccinations 
    })

@login_required
def add_pregnancy(request, mother_id):
    mother = get_object_or_404(Mother, id=mother_id)

    if request.method == 'POST':
        # NOTE: Using a ModelForm will simplify this:
        form = PregnancyForm(request.POST) 
        if form.is_valid():
            pregnancy = form.save(commit=False)
            pregnancy.mother = mother
            pregnancy.save()
            return redirect('motherPage', pk=mother.id)
    else:
        # Pass initial data if required (e.g., for subsequent pregnancies)
        form = PregnancyForm() 

    return render(request, 'Mom/pregnancy_form.html', {
        'form': form, 
        'mother': mother,
        'action_verb': 'Add' # For template title consistency
    })