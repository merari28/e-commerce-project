from django.shortcuts import render, redirect
from accounts.forms import RegistrationForm
from .models import Account
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


def register(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if Account.objects.filter(email=email).exists():
                messages.error(request, 'El email ya está registrado')
                return render(request, 'accounts/register.html', {'form': form})

            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )

            user.phone_number = phone_number
            user.save()

            messages.success(request, 'Usuario creado correctamente')
            form = RegistrationForm() 
            return render(request, 'accounts/register.html', {'form': form})

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso')
            return redirect('home')
        else:
            messages.error(request, 'Credenciales inválidas')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    
    return redirect('login')