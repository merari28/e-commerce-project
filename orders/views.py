import datetime
import json

from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse  

from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template

from carts.models import CartItem
from .models import Order, OrderProduct, Payment
from .forms import OrderForm

from xhtml2pdf import pisa


@login_required(login_url='login')
def payments(request):
    if request.method == 'POST':
        body = json.loads(request.body)

        order_number = request.session.get('order_number')

        try:
            order = Order.objects.get(
                user=request.user,
                is_ordered=False,
                order_number=order_number
            )
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        cart_items = CartItem.objects.filter(user=request.user)


        for item in cart_items:
            if item.product.stock < item.quantity:
                return JsonResponse({
                    'error': f'Stock insuficiente para {item.product.product_name}'
                })


        payment = Payment.objects.create(
            user=request.user,
            payment_id=body.get('transID'),
            payment_method=body.get('payment_method'),
            amount_paid=order.order_total,
            status=body.get('status'),
        )

        order.payment = payment
        order.is_ordered = True
        order.save()


        for item in cart_items:
            product = item.product

            orderproduct = OrderProduct.objects.create(
                order_id=order.id,
                payment=payment,
                user_id=request.user.id,
                product_id=item.product_id,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True,
            )

            variations = item.variations.all()
            orderproduct.variation.set(variations)

            product.stock -= item.quantity
            product.save()


        cart_items.delete()

        orderproducts = OrderProduct.objects.filter(order=order)


        mail_subject = 'Confirmación de compra'

        message = render_to_string('orders/order_email.html', {
            'order': order,
            'orderproducts': orderproducts,
        })

        to_email = order.email

        send_email = EmailMessage(
            mail_subject,
            message,
            to=[to_email]
        )

        send_email.content_subtype = "html"

        try:
            send_email.send(fail_silently=False)
        except Exception as e:
            print(e)

        return JsonResponse({
            'url': reverse('order_complete')
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='login')
def place_order(request, total=0, quantity=0):

    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            current_date = datetime.date.today().strftime("%Y%m%d")
            order_number = current_date + str(data.id)

            data.order_number = order_number
            data.save()

            request.session['order_number'] = order_number

            try:
                order = Order.objects.get(
                    user=current_user,
                    is_ordered=False,
                    order_number=order_number
                )
            except Order.DoesNotExist:
                return redirect('checkout')

            order_total_str = format(order.order_total, '.2f')

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'order_total_str': order_total_str,
            }

            return render(request, 'orders/payments.html', context)

        else:
            return redirect('checkout')

    return redirect('checkout')


@login_required(login_url='login')
def order_complete(request):
    order_number = request.session.get('order_number')

    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return redirect('store')

    orderproducts = OrderProduct.objects.filter(order=order)


    for item in orderproducts:
        item.subtotal = float(item.product_price) * item.quantity

    context = {
        'order': order,
        'orderproducts': orderproducts,
    }

    return render(request, 'orders/order_complete.html', context)


@login_required(login_url='login')
def download_invoice(request, order_number):
    try:
        order = Order.objects.get(
            order_number=order_number,
            user=request.user
        )
    except Order.DoesNotExist:
        return redirect('store')

    orderproducts = OrderProduct.objects.filter(order=order)

    template = get_template('orders/invoice.html')
    html = template.render({
        'order': order,
        'orderproducts': orderproducts
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{order_number}.pdf'

    result = pisa.CreatePDF(html, dest=response)

    if result.err:
        return HttpResponse("Error generando PDF", status=500)

    return response


