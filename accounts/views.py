import requests

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile

from carts.models import Cart, CartItem
from carts.views import _cart_id

from orders.models import Order
from store.models import ReviewRating

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


def register(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data.get('password') or form.cleaned_data.get('password1')

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
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activa tu cuenta'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            send_email = EmailMessage(mail_subject, message, to=[email])
            send_email.send(fail_silently=False)

            return redirect(f'/accounts/login/?command=verification&email={email}')

    return render(request, 'accounts/register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Cuenta activada correctamente')
        return redirect('login')

    messages.error(request, 'Link de activación inválido')
    return redirect('register')


def login_view(request):
    command = request.GET.get('command')
    email = request.GET.get('email')

    if command == 'verification':
        messages.success(request, f'Te enviamos un correo a {email}')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None and user.is_active:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)

                    product_variation = []

                    for item in cart_items:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)

                    existing_variation_list = []
                    cart_item_ids = []

                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation))
                        cart_item_ids.append(item.id)

                    for pr in product_variation:
                        if pr in existing_variation_list:
                            index = existing_variation_list.index(pr)
                            item_id = cart_item_ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_items = CartItem.objects.filter(cart=cart)

                            for item in cart_items:
                                item.user = user
                                item.save()

            except Exception:
                pass

            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso')

            url = request.META.get('HTTP_REFERER')

            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))

                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)

            except Exception:
                return redirect('dashboard')

            return redirect('dashboard')

        messages.error(request, 'Credenciales inválidas')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):

    orders_count = Order.objects.filter(
        user=request.user,
        is_ordered=True
    ).count()

    userprofile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    user_reviews = ReviewRating.objects.filter(
        user=request.user,
        status=True
    )

    reviews_count = user_reviews.count()

    average_rating = user_reviews.aggregate(
        Avg('rating')
    )['rating__avg']

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
        'reviews_count': reviews_count,
        'average_rating': average_rating,
    }

    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user,
        is_ordered=True
    ).order_by('-created_at')

    context = {
        'orders': orders,
    }

    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        user_form = UserForm(
            request.POST,
            instance=request.user
        )

        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=userprofile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(
                request,
                'Perfil actualizado correctamente.'
            )

            return redirect('edit_profile')

    else:
        user_form = UserForm(instance=request.user)

        profile_form = UserProfileForm(
            instance=userprofile
        )

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }

    return render(
        request,
        'accounts/edit_profile.html',
        context
    )


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Restablecer contraseña'
            body = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            send_email = EmailMessage(mail_subject, body, to=[email])
            send_email.send(fail_silently=False)

            messages.success(request, 'Se ha enviado un correo para restablecer tu contraseña')
            return redirect('login')

        messages.error(request, 'El correo no existe')

    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Por favor resetea tu password')
        return redirect('resetPassword')

    messages.error(request, 'El link ha expirado')
    return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, 'Contraseña restablecida correctamente')
            return redirect('login')

        messages.error(request, 'Las contraseñas no coinciden')
        return redirect('resetPassword')

    return render(request, 'accounts/resetPassword.html')


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(
            user=request.user,
            data=request.POST
        )

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            messages.success(
                request,
                'Tu contraseña fue actualizada correctamente.'
            )

            return redirect('change_password')
    else:
        form = PasswordChangeForm(user=request.user)

    context = {
        'form': form,
    }

    return render(request, 'accounts/change_password.html', context)