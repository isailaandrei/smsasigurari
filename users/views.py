from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView


@method_decorator(login_required, name='dispatch')
class RegisterView(FormView):

    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = '/login'

    def form_valid(self, form):
        messages.success(self.request, f'Contul dumneavoastra a fost creat!')
        form.save()
        return super().form_valid(form)