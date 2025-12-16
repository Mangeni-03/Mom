# Mom/admin.py

from django.contrib import admin
from .models import Mother, Pregnancy, Child, Vaccination, ChildVaccination
from django.utils.html import format_html, mark_safe 
from django.utils import timezone 

# --- INLINE CLASSES ---
class PregnancyInline(admin.TabularInline):
    model = Pregnancy
    extra = 0
    fields = ('due_date', 'next_visit', 'created_at')
    readonly_fields = ('created_at',)
    date_hierarchy = 'due_date'

class ChildInline(admin.TabularInline):
    model = Child
    extra = 0 
    fields = ('name', 'dob', 'gender')
    readonly_fields = ('dob',) 

class ChildVaccinationInline(admin.TabularInline):
    model = ChildVaccination
    extra = 0
    fields = ('vaccination', 'scheduled_date', 'completed', 'completion_date')
    readonly_fields = ('scheduled_date', 'completion_date')

# --- CUSTOM ACTIONS ---
@admin.action(description='Mark selected vaccinations as completed')
def mark_completed(modeladmin, request, queryset):
    """Marks selected ChildVaccination records as completed today."""
    queryset.filter(completed=False).update(
        completed=True,
        completion_date=timezone.localdate()
    )
    modeladmin.message_user(
        request, 
        f"Successfully marked {queryset.count()} vaccinations as completed.", 
        level='success'
    )


# --- ADMIN CLASSES ---
@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'hospital', 'language', 'consent_display', 'get_current_status', 'created_at')
    search_fields = ('name', 'phone', 'hospital')
    list_filter = ('hospital', 'language', 'consent') 
    date_hierarchy = 'created_at' 
    inlines = [PregnancyInline, ChildInline] # <-- ADDED
    
    fieldsets = (
        ('Personal Information', {
            'fields': (('name', 'phone'), 'language', 'hospital'),
        }),
        ('Consent and Status', {
            'fields': ('consent', 'created_at'),
            'description': 'Consent must be granted to send automated reminders.',
        })
    )
    readonly_fields = ('created_at',)

    def consent_display(self, obj):
        if obj.consent:
            return mark_safe('<span style="color: green;">&#10004; YES</span>')
        return mark_safe('<span style="color: red;">&#10006; NO</span>')
    consent_display.short_description = 'Consent'
    
    def get_current_status(self, obj):
        return obj.get_current_status()
    get_current_status.short_description = 'Current Status'


@admin.register(Pregnancy)
class PregnancyAdmin(admin.ModelAdmin):
    list_display = ('mother_name', 'due_date', 'next_visit', 'is_active')
    search_fields = ('mother__name', 'due_date')
    list_filter = ('due_date', 'next_visit')
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Mother & Core Dates', {
            'fields': ('mother', 'due_date', 'next_visit'),
        }),
        ('Administration', {
            'fields': ('created_at',),
            'classes': ('collapse',), 
        })
    )
    readonly_fields = ('created_at',)
    
    def mother_name(self, obj):
        return obj.mother.name
    mother_name.short_description = 'Mother'
    
    def is_active(self, obj):
        return obj.due_date and obj.due_date >= timezone.localdate()
    is_active.boolean = True
    is_active.short_description = 'Active Pregnancy'


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'mother', 'dob', 'gender', 'age_display')
    search_fields = ('name', 'mother__name') 
    list_filter = ('gender', 'dob')
    date_hierarchy = 'dob'
    inlines = [ChildVaccinationInline] # <-- ADDED

    def age_display(self, obj):
        return obj.get_age_display() if hasattr(obj, 'get_age_display') else "N/A"
    age_display.short_description = 'Age'


@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'dose_order', 'recommended_age_days')
    list_filter = ('dose_order',)
    search_fields = ('name',)


@admin.register(ChildVaccination)
class ChildVaccinationAdmin(admin.ModelAdmin):
    list_display = ('child_name', 'vaccination_name', 'scheduled_date', 'completed_display', 'completion_date')
    search_fields = ('child__name', 'vaccination__name')
    list_filter = ('completed', 'scheduled_date')
    date_hierarchy = 'scheduled_date'
    actions = [mark_completed] # <-- ADDED
    
    def child_name(self, obj):
        return obj.child.name
    child_name.short_description = 'Child'
    
    def vaccination_name(self, obj):
        return obj.vaccination.name
    vaccination_name.short_description = 'Vaccine'

    def completed_display(self, obj):
        if obj.completed:
            return mark_safe('<span style="color: green; font-weight: bold;">YES</span>')
        return mark_safe('<span style="color: red;">NO</span>')
    completed_display.short_description = 'Completed'