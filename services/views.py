from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.urls import reverse

from django.db.models import Count
from django.db.models import Q
from django.contrib import messages

from services.models import Service, Subscription
from categories.models import Category
from comments.models import Comment
from accounts.models import UserProfile

from django import forms
from services.forms import AddServiceForm
from accounts.forms import AddSubscriptionForm, AddSubscriptionFromDetailForm
from comments.forms import CommentForm

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from django.views import View
from django.views.generic import View, TemplateView, DetailView, FormView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import SingleObjectMixin

class HomeView(View):
	def get(self, request, *args, **kwargs):
		services = Service.objects.all()
		categories = Category.objects.all()
		cat_count = len(categories)
		categories = Category.objects.all().annotate(num_cats=Count('service')).order_by('-num_cats')
		categories = categories[:6]
		people = UserProfile.objects.all()[:6]
		featured = Service.objects.filter(featured=True)[:3]
		popular = Service.objects.annotate(num_users=Count('subscription_service')).order_by('-num_users')[:3]
		new = Service.objects.order_by('-date_created')[:3]
		context = {
			'featured':featured,
			'popular':popular,
			'new':new,
			'categories':categories,
			'cat_count':cat_count,
			'people':people,
		}
		return render(request, 'services/home.html', context)

def services(request):


	services = Service.objects.all().order_by('-date_created')
	context = {'services':services}
	query = request.GET.get('q')

	if query:
		queryset_list = services.filter(
			Q(service_name__icontains=query) |
			Q(description_short__icontains=query) |
			Q(description_long__icontains=query) |
			Q(emoji__icontains=query) |
			Q(tags__name__in=[query])
			).distinct()

		context['services'] = queryset_list


	return render(request, 'services/services.html', context)

def add_service_view(request):

	form = AddServiceForm(request.POST or None)
	context = {
		'form':form,
	}

	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		return redirect(reverse('services:add_service_from_detail_view', kwargs={'service_slug':instance.service_slug,}))

	return render(request, 'services/add_service.html', context)

class AddServiceView(TemplateView):
	template_name = 'services/add_service.html'

	def get(self, request):
		form = AddServiceForm()

		args = {'form':form}
		return render(request, self.template_name, args)

	def post(self, request):
		form = AddServiceForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.user = request.user
			post.save()

			return redirect('services:services')

		args = {'form':form,}
		return render(request, self.template_name, args)


def service_detail(request, service_slug):
	instance = get_object_or_404(Service, service_slug=service_slug)
	initial_data = {
		'content_type':instance.get_content_type,
		'object_id':instance.id
	}
	form = CommentForm(request.POST or None, initial=initial_data)
	subscribers = Subscription.objects.filter(service=instance, private=False, wishlist=False)
	subscribers_count = subscribers.distinct().count()
	subscribers = subscribers[:6]
	comments = instance.comments

	context = {
		'instance':instance,
		'form':form,
		'subscribers':subscribers,
		'subscribers_count':subscribers_count,
		'comments':comments,
	}
	if request.user.is_authenticated():
		user_info = Subscription.objects.filter(service=instance, user=request.user.userprofile).first()
		context['user_info'] = user_info

	if form.is_valid():
		c_type = form.cleaned_data.get("content_type")
		content_type = ContentType.objects.get(model=c_type)
		obj_id = form.cleaned_data.get('object_id')
		content_data = form.cleaned_data.get('content')
		comment_emoji = form.cleaned_data.get('emoji')
		parent_obj = None
		try:
			parent_id = int(request.POST.get("parent_id"))
		except:
			parent_id = None

		if parent_id:
			parent_qs = Comment.objects.filter(id=parent_id)
			if parent_qs.exists():
				parent_obj = parent_qs.first()

		new_comment, created = Comment.objects.get_or_create(
			user=request.user,
			content_type=content_type,
			object_id=obj_id,
			content=content_data,
			parent=parent_obj,
			emoji=comment_emoji,
		)
		messages.success(request, 'Your comment was added!')
		return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

	return render(request, 'services/service_detail.html', context)


class ServiceDetailView(TemplateView):

	def get(self, request, *arg, **kwargs):
		view = ServiceView.as_view()
		return view(request, *arg, **kwargs)

	def post(self, request, *args, **kwargs):
		view = ServiceComment.as_view()
		return view(request, *args, **kwargs)

def service_subscribers(request, service_slug):
	service = Service.objects.get(service_slug=service_slug)
	subscriber_list = Subscription.objects.filter(service=service, private=False, wishlist=False)

	context = {
		'subscriber_list':subscriber_list,
		'service':service,
	}

	return render(request, 'services/service_subscriber_list.html', context)

class ServiceSubscriberListView(TemplateView):

	template_name = 'services/service_subscriber_list.html'

	def get_context_data(self, **kwargs):
		context = super(ServiceSubscriberListView, self).get_context_data(**kwargs)
		context['subscriber_list'] = Subscription.objects.filter(service=self.kwargs['pk']).distinct()
		context['service'] = Service.objects.filter(id=self.kwargs['pk'])
		return context

@login_required
def add_service_from_detail_view(request, service_slug):
	service = Service.objects.get(service_slug=service_slug)
	if request.user.is_authenticated():

		initial = {
			'service':service,
			'bucksamonth':service.bucksamonth,
		}
		form = AddSubscriptionFromDetailForm(request.POST or None, initial=initial)

		if request.method=="POST":
			if form.is_valid():
				instance = form.save(commit=False)
				instance.user = request.user.userprofile
				instance.save()
				return redirect('accounts:profile')

		context = {
			'form':form,
			'service':service,
		}

		return render(request, 'services/add_service_from_detail_view.html', context)

	else:
		messages.success(request, "Please login")
		return redirect('accounts:login')
