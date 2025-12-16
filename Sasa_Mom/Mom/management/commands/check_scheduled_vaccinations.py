from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from Mom.models import ChildVaccination

class Command(BaseCommand):
    help = "Check all scheduled child vaccinations (auto-detect reminder fields)"

    def handle(self, *args, **options):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        vaccinations = ChildVaccination.objects.select_related(
            "child", "child__mother", "vaccination"
        )

        if not vaccinations.exists():
            self.stdout.write("❌ No scheduled vaccinations found.")
            return

        self.stdout.write("\n📋 ALL SCHEDULED VACCINATIONS\n")

        for cv in vaccinations:
            status = "✅ COMPLETED" if cv.completed else "⏳ PENDING"

            # 🔁 AUTO-DETECT REMINDER FIELDS
            if hasattr(cv, "reminder_day_before_sent"):
                reminder_status = (
                    f"Day-before: {'📨 SENT' if cv.reminder_day_before_sent else '❌ NOT SENT'} | "
                    f"On-day: {'📨 SENT' if cv.reminder_on_day_sent else '❌ NOT SENT'}"
                )
            elif hasattr(cv, "reminder_sent"):
                reminder_status = "📨 SENT" if cv.reminder_sent else "❌ NOT SENT"
            else:
                reminder_status = "⚠️ No reminder fields"

            due_flag = ""
            if cv.scheduled_date in [today, tomorrow] and not cv.completed:
                due_flag = "🔥 DUE NOW"

            self.stdout.write(
                f"""
Child: {cv.child.name or 'Child'}
Mother: {cv.child.mother.name} ({cv.child.mother.phone})
Vaccine: {cv.vaccination.name}
Scheduled Date: {cv.scheduled_date}
Status: {status}
Reminder: {reminder_status}
{due_flag}
----------------------------------------
"""
            )

        due_count = vaccinations.filter(
            scheduled_date__in=[today, tomorrow],
            completed=False
        ).count()

        self.stdout.write(f"\n🔔 Vaccinations due today or tomorrow: {due_count}")
