from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import ListView, DetailView, CreateView, FormView
from .models import *
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse

from .forms import *
from .utils import *


class BlogHome(DataMixin, ListView):
    model = Blog
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Главная страница')
        context.update(c_def)
        return context

    def get_queryset(self):
        return Blog.objects.filter(is_published=True).select_related('cat')


class ShowPost(DataMixin, DetailView):
    model = Blog
    template_name = 'blog/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=context['post'])
        context.update(c_def)
        return context


class BlogCategory(DataMixin, ListView):
    model = Blog
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Blog.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория - ' + str(category.name), cat_selected=category.pk)
        context.update(c_def)
        return context


class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'blog/addpage.html'
    success_url = reverse_lazy('index')
    login_url = reverse_lazy('index')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Добавление статьи')
        context.update(c_def)
        return context


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'blog/register.html'
    # success_url = reverse_lazy('login')
    # login_url = reverse_lazy('index')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Регистрация')
        context.update(c_def)
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('index')


class LoginUser(DataMixin, LoginView):

    form_class = AuthenticationForm
    template_name = 'blog/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизация')
        context.update(c_def)
        return context


class LogoutUser(DataMixin, LogoutView):

    template_name = 'blog/logout.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context.update(c_def)
        return context


class ContactFormView(DataMixin, FormView):

    form_class = ContactForm
    template_name = 'blog/contact.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Обратная связь')
        context.update(c_def)
        return context

    def form_valid(self, form):

        subject = 'Message'
        body = {
            'name': form.cleaned_data['name'],
            'email': form.cleaned_data['email'],
            'content': form.cleaned_data['content'],
        }

        message = '\n'.join(body.values())

        try:
            send_mail(subject, message, body['name'], ['admin@localhost'])
        except BadHeaderError:
            return HttpResponse('Найден некорректный заголовок')

        if form.is_valid():
            print(form.cleaned_data)
        else:
            form = ContactForm()
        return redirect('index')

