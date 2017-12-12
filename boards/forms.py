from django import forms
from .models import Languages, FamilyProcessor


language_obj = Languages.objects.all()
family_obj = FamilyProcessor.objects.all()

STAKEHOLDERS = ['Beginner', 'Professional']
STAKEHOLDERS_CHOICES = [(i.lower(), i) for i in STAKEHOLDERS]


class RequirementsForm(forms.Form):
    knowledge_level = forms.ChoiceField(choices=STAKEHOLDERS_CHOICES)

    analog = forms.IntegerField(min_value=1, required=False)
    digit = forms.IntegerField(min_value=1, required=False)
    voltage = forms.DecimalField(min_value=1, max_value=10, required=False)
    processor_family = forms.ModelChoiceField(queryset=family_obj, required=False)

    language = forms.ModelChoiceField(queryset=language_obj, required=False)

    price = forms.DecimalField(min_value=0, decimal_places=2, required=False)
    form = forms.IntegerField(required=False)
