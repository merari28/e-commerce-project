"""Verify SMTP connectivity and send demo emails to the target inbox.

Sends:
  1. A styled welcome email.
  2. An order-confirmation email rendered from the real order template,
     using the most recent demo order.

Usage:
    USE_SQLITE=1 venv/Scripts/python.exe scripts/send_demo_emails.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string

from orders.models import Order, OrderProduct

TO = "merarivillalba@gmail.com"


def send_welcome(connection):
    html = """
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:600px;margin:auto;
                border:1px solid #eee;border-radius:12px;overflow:hidden">
      <div style="background:linear-gradient(135deg,#2563eb,#1e293b);padding:32px;color:#fff">
        <h1 style="margin:0">KcerBlack / Merari Store</h1>
        <p style="margin:8px 0 0;opacity:.85">Tu tienda online de tecnologia y moda</p>
      </div>
      <div style="padding:32px;color:#222">
        <h2>Bienvenida 👋</h2>
        <p>Este es un correo de demostracion enviado desde el proyecto e-commerce
           (Django 6) que esta corriendo localmente.</p>
        <p>El catalogo, los usuarios, los pedidos y los pagos demo ya estan cargados
           y funcionando.</p>
        <p style="margin-top:24px">
          <a href="#" style="background:#2563eb;color:#fff;padding:12px 22px;
             border-radius:8px;text-decoration:none">Ir a la tienda</a>
        </p>
      </div>
      <div style="background:#f8fafc;padding:16px 32px;color:#64748b;font-size:13px">
        © KcerBlack — correo automatico de demostracion.
      </div>
    </div>
    """
    msg = EmailMessage(
        "✅ Demo Merari Store — bienvenida y correo de prueba",
        html,
        settings.DEFAULT_FROM_EMAIL,
        [TO],
        connection=connection,
    )
    msg.content_subtype = "html"
    msg.send(fail_silently=False)
    print("  [ok] welcome email sent to", TO)


def send_order(connection):
    order = Order.objects.filter(is_ordered=True).order_by("-created_at").first()
    if not order:
        print("  [skip] no completed order found for order email")
        return
    orderproducts = OrderProduct.objects.filter(order=order)
    html = render_to_string(
        "orders/order_email.html",
        {"order": order, "orderproducts": orderproducts},
    )
    msg = EmailMessage(
        f"🧾 Confirmacion de compra — pedido {order.order_number}",
        html,
        settings.DEFAULT_FROM_EMAIL,
        [TO],
        connection=connection,
    )
    msg.content_subtype = "html"
    msg.send(fail_silently=False)
    print(f"  [ok] order confirmation ({order.order_number}) sent to {TO}")


if __name__ == "__main__":
    print("Connecting to SMTP host:", settings.EMAIL_HOST)
    conn = get_connection()
    conn.open()  # raises if auth/connectivity fails
    print("  [ok] SMTP connection established")
    send_welcome(conn)
    send_order(conn)
    conn.close()
    print("All demo emails sent successfully.")
