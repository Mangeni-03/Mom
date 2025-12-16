from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
# Create your models here.
  
from django.db import models
from django.utils import timezone

class Mother(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, help_text="Format 07..or 01...or +254....")
    language = models.CharField(max_length=50, default='en')
    consent = models.BooleanField(db_default=False)
    hospital = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} — {self.phone}"
        
    def get_current_status(self):
        """
        Determines the mother's current status based on child and pregnancy records.
        """
        # 1. Check for existing children
        if self.children.exists():
            return "Child Born (Post-Natal Care)"

        # 2. Check current pregnancy status
        pregnancy = self.pregnancies.order_by('-id').first() 
        
        if pregnancy:
            today = timezone.localdate()
            
            # Antenatal Status
            if pregnancy.due_date and pregnancy.due_date >= today:
                return "Pregnant (Antenatal Care)"
            
            # Due Date Passed Status
            if pregnancy.due_date and pregnancy.due_date < today:
                return "Due Date Passed / Post-Natal Checkup"

        # 3. Default/Fallback Status
        return "New Registration / Status Pending"
class Pregnancy(models.Model):
    mother = models.ForeignKey(Mother, on_delete=models.CASCADE, related_name='pregnancies')
    due_date = models.DateField(null=True, blank=True)
    next_visit = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pregnancy for {self.mother.name} (due {self.due_date})"
    
class Child(models.Model):
    GENDER_CHOICES=[
        ('Male','Male'),
        ('Female','Female'),
        
    ]
    mother = models.ForeignKey(Mother, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=255, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES,default='Female')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or 'Child'} — {self.mother.name}"
    
class Vaccination(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    recommended_age_days = models.IntegerField(help_text='Recommended age in days')
    dose_order = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name} (dose {self.dose_order}) — {self.recommended_age_days} days"
    
class ChildVaccination(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='vaccinations')
    vaccination = models.ForeignKey(Vaccination, on_delete=models.PROTECT)
    scheduled_date = models.DateField(null=True, blank=True)

    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    reminder_day_before_sent = models.BooleanField(default=False)
    reminder_on_day_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    
class ScheduledVaccination(models.Model):
    mother = models.ForeignKey(Mother, on_delete=models.CASCADE)
    vaccination = models.ForeignKey(Vaccination, on_delete=models.CASCADE)
    due_date = models.DateField()
    notified = models.BooleanField(default=False)
