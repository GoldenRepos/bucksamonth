from django import forms
from services.models import Service


class AddServiceForm(forms.ModelForm):
	service_name = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "what's the service called?",
		}))

	url_name = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "what's the link?",
		}))


	description_long = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "describe it 140 characters or less",
		}))


	description_short = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "tell us about it in more detail",
		}))

	bucksamonth = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "how many bucks a month?",
		}))

	emoji = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "control + command + spacebar for emoji menu 😉",
		}))


	twitter = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "@twitter_handle",
		}))

	class Meta:
		model = Service
		fields = (
			'service_name',
			'url_name',
			'description_long',
			'description_short',
			'bucksamonth',
			'emoji',
			'twitter',
		)
