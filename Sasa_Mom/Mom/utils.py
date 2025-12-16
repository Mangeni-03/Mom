# Mom/utils.py (Final Corrected Version)

from datetime import timedelta
from django.utils import timezone
from .models import Child, Vaccination, ChildVaccination

def schedule_initial_vaccinations(child):
    """
    Schedules all required vaccinations for a new child based on their DOB
    and the recommended ages in the Vaccination model.
    """
    if not child.dob:
        # Cannot schedule without a date of birth
        return 0 

    vaccinations = Vaccination.objects.all()
    today = timezone.localdate()
    created_count = 0

    print(f"--- START SCHEDULING for {child.name} (DOB: {child.dob}) ---")

    for vac in vaccinations:
        # Calculate scheduled date: DOB + recommended_age_days
        # Assuming recommended_age_days is 0 for 'at birth' vaccines
        scheduled_date = child.dob + timedelta(days=vac.recommended_age_days)

        # Print every calculated schedule date for debugging
        print(f"Checking {vac.name} (Age: {vac.recommended_age_days} days). Scheduled Date: {scheduled_date}")

        # FIX APPLIED: Change > to >= to include 'at birth' vaccines scheduled for today.
        if scheduled_date >= today: 
            # Check if this vaccination/dose is not already scheduled for this child
            exists = ChildVaccination.objects.filter(
                child=child,
                vaccination=vac,
                completed=False
            ).exists()

            if not exists:
                ChildVaccination.objects.create(
                    child=child,
                    vaccination=vac,
                    scheduled_date=scheduled_date,
                    completed=False,
                    reminder_day_before_sent=False,
                    reminder_on_day_sent=False
                )
                # Print when a record is successfully created
                print(f"SUCCESS: Created schedule for {vac.name} on {scheduled_date}")
                created_count += 1
            else:
                print(f"SKIPPED: {vac.name} already exists.")
        else:
            print(f"SKIPPED: {vac.name} is in the past ({scheduled_date}).")

    print(f"--- END SCHEDULING. Total created: {created_count} ---")
    return created_count