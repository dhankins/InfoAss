from django import forms
from fileaccess.models import RWAttribute

class AccessLoginForm(forms.Form):
	username = forms.CharField(
		max_length=50, 
		widget=forms.TextInput(), 
		error_messages={'required' : 'You must enter a username!'}
	)
	password = forms.CharField(
		max_length=50, 
		widget=forms.PasswordInput(), 
		error_messages={'required' : 'You must enter a password!'}
	)

class NewFileForm(forms.Form):
	CHOICES = ((att.pk, att.identifier) for att in RWAttribute.objects.all())

	fileName = forms.CharField(
		max_length=100, 
		error_messages={'required' : 'You must enter a file name!'}
	)
	fileUpload = forms.FileField(
		error_messages={'required' : 'You must choose a file!'}
	)
	attributes = forms.MultipleChoiceField(
		choices=CHOICES,  
		widget=forms.CheckboxSelectMultiple(), 
		required=False
	)

class UpdateFileForm(forms.Form):
	CHOICES = ((att.pk, att.identifier) for att in RWAttribute.objects.all())

	fileName = forms.CharField(
		max_length=100, 
		error_messages={'required' : 'You must have a file name!'}
	)
	fileUpload = forms.FileField(
		required=False
	)
	attributes = forms.MultipleChoiceField(
		choices=CHOICES, 
		widget=forms.CheckboxSelectMultiple(), 
		required=False
	)