from django import forms
from .models import Mother, Pregnancy,Vaccination, ChildVaccination,Child


class MotherForm(forms.ModelForm):
    class Meta:
        model = Mother
        fields = ['name', 'phone', 'language', 'consent', 'hospital']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital': forms.TextInput(attrs={'class': 'form-control'}),
            'consent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PregnancyForm(forms.ModelForm):
    class Meta:
        model = Pregnancy
        fields = ['due_date', 'next_visit']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'next_visit': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class MotherPregnancyForm(forms.Form):
    """
    Combines both MotherForm + PregnancyForm into one big form.
    """
    # Mother fields
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    language = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    hospital = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Pregnancy fields
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    already_given_birth = forms.BooleanField(
        required=False,
        label="Already Given Birth",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    next_visit = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    # Mom consent
    consent = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get('due_date')
        already_given_birth = cleaned_data.get('already_given_birth')

        # Ensure either due_date or already_given_birth is provided
        if not due_date and not already_given_birth:
            raise forms.ValidationError("Please provide a due date or check 'Already Given Birth'.")

        return cleaned_data

    def save(self):
        """
        Save both models and attach the conditional flag to the returned Mother object.
        """
        # Get the flag state
        already_given_birth_flag = self.cleaned_data.get('already_given_birth', False)

        # 1. Save Mother
        mother = Mother.objects.create(
            name=self.cleaned_data['name'],
            phone=self.cleaned_data['phone'],
            language=self.cleaned_data['language'],
            hospital=self.cleaned_data['hospital'],
            consent=self.cleaned_data.get('consent', False),
           
        )
        
    
        mother.already_given_birth = already_given_birth_flag


        # 2. Save Pregnancy
        Pregnancy.objects.create(
            mother=mother,
            # Set due_date to None if 'already_given_birth' is ticked
            due_date=None if already_given_birth_flag else self.cleaned_data.get('due_date'),
            next_visit=self.cleaned_data.get('next_visit')
        )

        return mother # Returns the mother object with the attached flag

    

class PregnancyNextVisitForm(forms.ModelForm):
    class Meta:
        model = Pregnancy
        fields = ['next_visit']
        widgets = {
            'next_visit': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['mother', 'name', 'dob', 'gender']
        widgets = {
            'mother': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }

class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = ['name', 'description', 'recommended_age_days', 'dose_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'recommended_age_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'dose_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ChildVaccinationForm(forms.ModelForm):
    class Meta:
        model = ChildVaccination
        fields = ['vaccination', 'scheduled_date', 'completed']
        widgets = {
            'vaccination': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
