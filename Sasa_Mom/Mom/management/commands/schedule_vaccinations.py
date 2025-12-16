from django.core.management.base import BaseCommand
from django.utils import timezone
from Mom.models import Child, Vaccination, ChildVaccination

class Command(BaseCommand):
    help = "Automatically schedule all vaccinations for all children based on DOB"

    def handle(self, *args, **options):
        today = timezone.now().date()
        children = Child.objects.all()
        vaccinations = Vaccination.objects.all()
        created_count = 0

        for child in children:
            if not child.dob:
                self.stdout.write(f"Skipping {child.name or 'Child'}: no DOB")
                continue

            for vac in vaccinations:
                # Calculate scheduled date based on recommended_age_days
                scheduled_date = child.dob + timezone.timedelta(days=vac.recommended_age_days)

                # Skip if date is in the past
                if scheduled_date < today:
                    continue

                # Check if already scheduled
                exists = ChildVaccination.objects.filter(
                    child=child,
                    vaccination=vac
                ).exists()

                if not exists:
                    ChildVaccination.objects.create(
                        child=child,
                        vaccination=vac,
                        scheduled_date=scheduled_date,
                        completed=False,
                        reminder_sent=False
                    )
                    created_count += 1
                    self.stdout.write(
                        f"Scheduled {vac.name} for {child.name or 'Child'} on {scheduled_date}"
                    )

        self.stdout.write(f"Total new vaccinations scheduled: {created_count}")
