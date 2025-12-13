from django.contrib import admin
from .models import Mother, Pregnancy, Child, Vaccination, ChildVaccination

# Register your models here.
# Manage models in the admin panel
@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'hospital', 'language', 'consent', 'created_at')
    search_fields = ('name',)

@admin.register(Pregnancy)
class PregnancyAdmin(admin.ModelAdmin):
    list_display = ('mother', 'due_date', 'next_visit')

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'mother', 'dob','gender')
    search_fields = ('name', 'mother__name') 

@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'dose_order', 'recommended_age_days')

@admin.register(ChildVaccination)
class ChildVaccinationAdmin(admin.ModelAdmin):
    list_display = ('child', 'vaccination', 'scheduled_date', 'completed')
