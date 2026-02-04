from django import forms
from django.contrib.auth import get_user_model
from .models import AssessmentTemplate, PatientAssessment

User = get_user_model()


class AssessmentTemplateForm(forms.ModelForm):
    """Form for creating/editing assessment templates"""
    
    class Meta:
        model = AssessmentTemplate
        fields = [
            'name', 'code', 'category', 'description',
            'max_score', 'min_score', 'higher_is_better',
            'score_interpretation', 'items', 'version',
            'status', 'applicable_roles'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '如: BARTHEL, MMSE'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'higher_is_better': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'score_interpretation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'items': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class PatientAssessmentForm(forms.ModelForm):
    """Form for conducting patient assessments"""
    
    class Meta:
        model = PatientAssessment
        fields = [
            'patient', 'template', 'assessment_date',
            'responses', 'total_score', 'interpretation',
            'clinical_notes', 'status',
            'related_care_plan', 'related_rehab_plan'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'template': forms.Select(attrs={'class': 'form-select'}),
            'assessment_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'responses': forms.HiddenInput(),  # Will be populated by JavaScript
            'total_score': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'interpretation': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'clinical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'related_care_plan': forms.Select(attrs={'class': 'form-select'}),
            'related_rehab_plan': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        patient_id = kwargs.pop('patient_id', None)
        super().__init__(*args, **kwargs)
        
        # Filter patients
        self.fields['patient'].queryset = User.objects.filter(
            role='patient', is_active=True
        )
        
        # Filter active templates only
        self.fields['template'].queryset = AssessmentTemplate.objects.filter(
            status='active'
        )
        
        # Pre-select patient if provided
        if patient_id:
            self.fields['patient'].initial = patient_id
            self.fields['patient'].widget.attrs['readonly'] = True
        
        # Make related fields optional and filter by patient
        self.fields['related_care_plan'].required = False
        self.fields['related_rehab_plan'].required = False


class AssessmentFilterForm(forms.Form):
    """Filter form for assessment list"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        required=False,
        empty_label='所有病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    template = forms.ModelChoiceField(
        queryset=AssessmentTemplate.objects.filter(status='active'),
        required=False,
        empty_label='所有評估類型',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    category = forms.ChoiceField(
        choices=[('', '所有類別')] + list(AssessmentTemplate.CATEGORY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', '所有狀態')] + list(PatientAssessment.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )