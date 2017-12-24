from django import forms
from .models import Languages, FamilyProcessor
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import BLANK_CHOICE_DASH


language_obj = Languages.objects.all()
family_obj = FamilyProcessor.objects.all()

STAKEHOLDERS = [_('Beginner'), _('Professional')]
STAKEHOLDERS_CHOICES = [(i.lower(), i) for i in STAKEHOLDERS]

FORM_FACTOR = [_('Small'), _('Medium'), _('Large')]
FORM_FACTOR_CHOICES = BLANK_CHOICE_DASH+[(i.lower(), i) for i in FORM_FACTOR]

VOLTAGE = ['3.3', '5', '12']
VOLTAGE_CHOICES = BLANK_CHOICE_DASH+[(i.lower(), i) for i in VOLTAGE]


class RequirementsForm(forms.Form):
    knowledge_level = forms.ChoiceField(choices=STAKEHOLDERS_CHOICES)

    analog = forms.IntegerField(min_value=1, required=False)
    digit = forms.IntegerField(min_value=1, required=False)
    voltage = forms.ChoiceField(choices=VOLTAGE_CHOICES, required=False)
    processor_family = forms.ModelChoiceField(queryset=family_obj, required=False)

    language = forms.ModelChoiceField(queryset=language_obj, required=False)

    price = forms.DecimalField(min_value=0, decimal_places=2, required=False)
    form = forms.ChoiceField(choices=FORM_FACTOR_CHOICES, required=False)
