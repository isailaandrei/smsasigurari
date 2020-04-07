from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


@method_decorator(login_required, name='dispatch')
class RegisterView(View):

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contul dumneavoastra a fost creat!')
            return redirect('login')
    
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'users/register.html', {'form': form})
