from django import forms
from django.forms import Select
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
	UserCreationForm,
	UserChangeForm,
	AuthenticationForm,
	ReadOnlyPasswordHashField,
	SetPasswordForm,
)

from services.models import Subscription, Service
from accounts.models import UserProfile
from django.contrib.auth import authenticate, login
import datetime

class UserLoginForm(forms.Form):
	username = forms.CharField(
		label='',
		widget=forms.TextInput(
			attrs={
			'class':'form-control',
			'placeholder': "enter your username",
	}))

	password = forms.CharField(
		label='',
		widget=forms.PasswordInput(
			attrs={
			'class':'form-control',
			'placeholder': "enter your password",
		}))


	def clean(self, *args, **kwargs):
		username = self.cleaned_data.get("username")
		password = self.cleaned_data.get("password")
		user = authenticate(username=username, password=password)
		user_qs = User.objects.filter(username=username)
		if user_qs.count() == 1:
			user = user_qs.first()
		if not user:
			raise forms.ValidationError("This user does not exist")
		if not user.check_password(password):
			raise forms.ValidationError("Incorrect password")

		if not user.is_active:
			raise forms.ValidationError("This user is no longer active")

		return super(UserLoginForm, self).clean(*args, **kwargs)




class MyAuthenticationForm(AuthenticationForm):

	username = forms.CharField(
		label='',
		widget=forms.TextInput(
			attrs={
			'class':'form-control',
			'placeholder': "enter your username",
		}))

	password = forms.CharField(
		label='',
		widget=forms.PasswordInput(
			attrs={
			'class':'form-control',
			'placeholder': "enter your password",
		}))


class RegistrationForm(UserCreationForm):
	email = forms.EmailField(
		required=True,
		widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "your email",
		}))

	username = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "pick a username for your public profile",
		}))

	first_name = forms.CharField(required=False, widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "your name (optional)",

		}))

	last_name = forms.CharField(required=False, widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "your last name (optional)",

		}))

	password1 = forms.CharField(widget=forms.PasswordInput(
		attrs={
		'class':'form-control',
		'placeholder': "choose a password",
		}))

	password2 = forms.CharField(widget=forms.PasswordInput(
		attrs={
		'class':'form-control',
		'placeholder': "type it again",
		}))


	class Meta:
		model = User
		fields = (
			'username',
			'email',
			'first_name',
			'last_name',
			'password1',
			'password2',
			)

	def save(self, commit=True):
		user = super(RegistrationForm, self).save(commit=False)
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.email = self.cleaned_data['email']

		if commit:
			user.save()

		return user



class EditPersonalInfoForm(forms.ModelForm):

	#setup = forms.BooleanField(widget=forms.HiddenInput)
	setup = forms.BooleanField(required=False, widget=forms.HiddenInput)

	description = forms.CharField(widget=forms.Textarea(
		attrs={

		'class':'form-control',
		'rows':3,
		'placeholder': "introduce yourself (required)",
		}))

	twitter = forms.CharField(required=False, widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "your twitter handle (optional)",
		}))

	emoji = forms.CharField(required=True, widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "choose your emojis (required)",
		}))

	facebook_url = forms.CharField(required=False, widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "facebook URL (optional)",
		}))

	linkedin_url = forms.CharField(required=False, widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "lnkedin URL (optional)",
		}))

	website = forms.CharField(required=False, widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "website URL (optional)",
		}))



	class Meta:
		model = UserProfile
		fields = (

			'description',
			'twitter',
			'emoji',
			'setup',
			'facebook_url',
			'linkedin_url',
			'website',

			)






class EditProfileForm(UserChangeForm):

	username = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "pick a username for your public profile",
		}))

	# email = forms.EmailField(
	# 	required=True,
	# 	widget=forms.TextInput(
	# 	attrs={
	# 	'class':'form-control',
	# 	'placeholder': "update your email address",
	# 	}))

	first_name = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "change your first name",
		}))

	last_name = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "update your last name",
		}))

	password = ReadOnlyPasswordHashField(label="Password",
		help_text="you can change your password "
			"using <a href=\"/account/profile/password/\">this form</a>.")


	class Meta:
		model = User
		fields = (
				'username',
				# 'email',
				'first_name',
				'last_name',
				# 'password',
				)

YEAR_CHOICES = tuple([2000+i for i in range(18)])


class AddSubscriptionForm(forms.ModelForm):

	service = forms.ModelChoiceField(
		queryset=Service.objects.order_by('service_name').extra(select={'lower_name':'lower(service_name)'}).order_by('lower_name'),
		widget=forms.Select(attrs={
			'class':'form-control',
			'placeholder':'select a subscrption service',
			})
		)

	cc_nickname = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "which credit card is it on (nickname)",
		}))

	bucksamonth = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "how many bucks a month?",
		}))


	private = forms.BooleanField(
		initial=False,
		required=False,
		widget=forms.CheckboxInput(

		attrs={

		}))



	wishlist = forms.BooleanField(
		initial=False,
		required=False,
		widget=forms.CheckboxInput(

		attrs={

		}))

	date_created = forms.DateField(
		initial=datetime.date.today,

		widget=forms.SelectDateWidget(

		years=YEAR_CHOICES))

	class Meta:
		model = Subscription
		fields = (

				'service',
				'cc_nickname',
				'bucksamonth',
				'private',
				'wishlist',
				'date_created'
				)


class AddSubscriptionFromDetailForm(forms.ModelForm):

	service = forms.ModelChoiceField(
		queryset=Service.objects.order_by('service_name').extra(select={'lower_name':'lower(service_name)'}).order_by('lower_name'),
		widget=forms.HiddenInput
		)

	cc_nickname = forms.CharField(
		required=False,
		widget=forms.TextInput(
			attrs={
			'class':'form-control',
			'placeholder': "which credit card is it on (nickname)",
		}))

	bucksamonth = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "how many bucks a month?",
		}))


	private = forms.BooleanField(
		initial=False,
		required=False,
		widget=forms.CheckboxInput(

		attrs={

		}))



	wishlist = forms.BooleanField(
		initial=False,
		required=False,
		widget=forms.CheckboxInput(

		attrs={

		}))

	date_created = forms.DateField(
		initial=datetime.date.today,

		widget=forms.SelectDateWidget(

		years=YEAR_CHOICES))

	class Meta:
		model = Subscription
		fields = (

				'service',
				'cc_nickname',
				'bucksamonth',
				'private',
				'wishlist',
				'date_created'
				)






class UpdateSubscriptionForm(forms.ModelForm):

	cc_nickname = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "which credit card is it on (nickname)",
		}))

	bucksamonth = forms.CharField(widget=forms.TextInput(
		attrs={
		'class':'form-control',
		'placeholder': "how many bucks a month?",
		}))

	date_created = forms.DateField(

		widget=forms.SelectDateWidget(
		attrs={
		},
		years=YEAR_CHOICES))

	private = forms.BooleanField(
		initial=False,
		required=False,
		widget=forms.CheckboxInput(

		attrs={

		}))



	wishlist = forms.BooleanField(
		required=False,
		widget=forms.CheckboxInput(
		attrs={
		}))

	class Meta:
		model = Subscription
		fields = (

				'cc_nickname',
				'bucksamonth',
				'private',
				'wishlist',
				'date_created',
				)
