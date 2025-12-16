from datetime import timedelta
from django.utils import timezone
from Mom.models import ChildVaccination
from Mom.utils.sms import send_sms
from Mom.utils.phone import format_phone

def send_vaccination_reminders():
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)

    vaccinations = ChildVaccination.objects.select_related(
        'child__mother',
        'vaccination'
    ).filter(
        completed=False,
        scheduled_date__in=[today, tomorrow],
        child__mother__consent=True
    )

    for cv in vaccinations:
        mother = cv.child.mother
        phone = format_phone(mother.phone)

        if cv.scheduled_date == tomorrow:
            message = (
                f"Hello {mother.name}, reminder: "
                f"{cv.child.name or 'your child'} is due for "
                f"{cv.vaccination.name} vaccination tomorrow."
            )
        else:
            message = (
                f"Hello {mother.name}, today is the vaccination day for "
                f"{cv.child.name or 'your child'} "
                f"({cv.vaccination.name}). "
                f"Please visit {mother.hospital}."
            )

        send_sms(phone, message)
