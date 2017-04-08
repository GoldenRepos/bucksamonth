from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.views.generic import View, TemplateView, DetailView, FormView, DeleteView
from django.views.generic.list import ListView
from services.models import Service, Comment, Subscription
from services.forms import AddServiceForm
from .forms import AddCommentForm
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.views.generic.detail import SingleObjectMixin
from django import forms
from django.views import View
from django.db.models import Count

# Create your views here.

class HomeView(View):
	def get(self, request, *args, **kwargs):
		services = Service.objects.all()
		featured = Service.objects.filter(featured=True)
		popular = Service.objects.annotate(num_users=Count('subscription_service')).order_by('-num_users')[:5]
		new = Service.objects.order_by('-date_created')[:5]
		context = {
			'featured':featured, 
			'popular':popular,
			'new':new, 
		}
		return render(request, 'services/home.html', context)

def services(request):
	services = Service.objects.all().order_by('-date_created')
	return render(request, 'services/services.html', {'services':services})


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

class ServiceView(DetailView):
	template_name = 'services/service_detail.html'
	model = Service

	def get_context_data(self, **kwargs):
		context = super(ServiceView, self).get_context_data(**kwargs)
		context['form'] = AddCommentForm()
		subscribers = Subscription.objects.filter(service=self.kwargs['pk'])
		context['subscribers'] = subscribers
		context['subscribers_count'] = subscribers.distinct().count()
		context['comments'] = Comment.objects.filter(service=self.kwargs['pk'])
		if self.request.user.is_authenticated:
			context['user_info'] = Subscription.objects.filter(service=self.kwargs['pk'], user=self.request.user.userprofile).first()
		return context


class ServiceComment(SingleObjectMixin, FormView):
	template_name = 'services/service_detail.html'
	form_class = AddCommentForm
	model = Service

	def post(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return HttpResponseForbidden()
		self.object = self.get_object()
		return super(ServiceComment, self).post(request, *args, **kwargs)

	def form_valid(self, form):
		#added in some extra bits here
		form.instance.user = self.request.user.userprofile
		form.instance.service = self.get_object()
		form.save()
		return super(ServiceComment, self).form_valid(form)

	def form_invalid(self, form, **kwargs):
		context = self.get_context_data(**kwargs)
		subscribers = Subscription.objects.filter(service=self.kwargs['pk'])
		context['subscribers'] = subscribers
		context['subscribers_count'] = subscribers.distinct().count()
		context['comments'] = Comment.objects.filter(service=self.kwargs['pk'])
		context['form'] = AddCommentForm()
		return self.render_to_response(context)

	def get_success_url(self):
		return reverse('services:service_detail', kwargs={'pk': self.object.pk})

class CommentDeleteView(DeleteView):

	model = Comment
	success_url = '/accounts/profile'

	def get_object(self, queryset=None):

		obj = super(CommentDeleteView, self).get_object()
		if not obj.user.user.id == self.request.user.id:
			raise Http404
		obj.delete()
		return obj

class ServiceDetailView(TemplateView):

	def get(self, request, *arg, **kwargs):
		view = ServiceView.as_view()
		return view(request, *arg, **kwargs)

	def post(self, request, *args, **kwargs):
		view = ServiceComment.as_view()
		return view(request, *args, **kwargs)

class ServiceSubscriberListView(TemplateView):
	
	template_name = 'services/service_subscriber_list.html'

	def get_context_data(self, **kwargs):
		context = super(ServiceSubscriberListView, self).get_context_data(**kwargs)
		context['subscriber_list'] = Subscription.objects.filter(service=self.kwargs['pk']).distinct()
		context['service'] = Service.objects.filter(id=self.kwargs['pk'])
		return context