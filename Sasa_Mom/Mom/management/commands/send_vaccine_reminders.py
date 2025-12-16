from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from twilio.rest import Client
from django.conf import settings
from Mom.models import ChildVaccination

class Command(BaseCommand):
    help = "Send vaccination reminders safely (no duplicates, auto-detect fields)"

    def handle(self, *args, **options):
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)

        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_number = settings.TWILIO_PHONE_NUMBER

        if not all([account_sid, auth_token, from_number]):
            self.stdout.write("❌ Twilio credentials missing")
            return

        client = Client(account_sid, auth_token)

        vaccinations = ChildVaccination.objects.select_related(
            "child", "child__mother", "vaccination"
        ).filter(completed=False)

        for cv in vaccinations:
            mother = cv.child.mother

            if hasattr(mother, "consent") and not mother.consent:
                continue

            phone = mother.phone.strip()
            if phone.startswith("07") or phone.startswith("01"):
                phone = "+254" + phone[1:]

            with transaction.atomic():
                cv = ChildVaccination.objects.select_for_update().get(id=cv.id)

                # Day-before reminder
                if cv.scheduled_date == tomorrow and not cv.reminder_day_before_sent:
                    message = f"Reminder: {cv.vaccination.name} vaccination for {cv.child.name or 'your child'} is TOMORROW."
                    try:
                        client.messages.create(body=message, from_=from_number, to=phone)
                        cv.reminder_day_before_sent = True
                        cv.save()
                        self.stdout.write(f"📨 Day-before reminder sent to {phone}")
                    except Exception as e:
                        self.stdout.write(f"❌ Failed to send SMS to {phone}: {e}")

                # On-day reminder
                elif cv.scheduled_date == today and not cv.reminder_on_day_sent:
                    message = f"Today is vaccination day for {cv.child.name or 'your child'} ({cv.vaccination.name})."
                    try:
                        client.messages.create(body=message, from_=from_number, to=phone)
                        cv.reminder_on_day_sent = True
                        cv.save()
                        self.stdout.write(f"📨 On-day reminder sent to {phone}")
                    except Exception as e:
                        self.stdout.write(f"❌ Failed to send SMS to {phone}: {e}")
