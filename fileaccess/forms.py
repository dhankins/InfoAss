from django import forms
from fileaccess.models import RWAttribute

class AccessLoginForm(forms.Form):
	username = forms.CharField(max_length=50, widget=forms.TextInput())
	password = forms.CharField(max_length=50, widget=forms.PasswordInput())

class NewFileForm(forms.Form):
	CHOICES = ((att.pk, att.identifier) for att in RWAttribute.objects.all())

	fileName = forms.CharField(max_length=100)
	fileUpload = forms.FileField()
	attributes = forms.MultipleChoiceField(choices=CHOICES, 
											widget=forms.CheckboxSelectMultiple(), 
											required=False)

class UpdateFileForm(forms.Form):
	CHOICES = ((att.pk, att.identifier) for att in RWAttribute.objects.all())

	fileName = forms.CharField(max_length=100)
	fileUpload = forms.FileField(required=False)
	attributes = forms.MultipleChoiceField(choices=CHOICES, 
											widget=forms.CheckboxSelectMultiple(), 
											required=False)