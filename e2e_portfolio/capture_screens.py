"""End-to-end screen capture for the Merari Store demo.

Drives a real browser through every screen of the app and saves full-page
screenshots into ./screenshots, suitable for a portfolio gallery.

Run (with the dev server already up on 127.0.0.1:8010):
    venv/Scripts/python.exe e2e_portfolio/capture_screens.py
"""
import os
import sys
import time

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8010")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(OUT, exist_ok=True)

# Demo credentials seeded by the data loader
USER_EMAIL = "pepe@gmail.com"
ADMIN_EMAIL = "admin@gmail.com"
PASSWORD = "Demo12345!"
ORDER_EMAIL = "merarivillalba@gmail.com"  # confirmation email recipient

results = []


def shot(page, name, full=True):
    path = os.path.join(OUT, name + ".png")
    page.wait_for_timeout(700)
    page.screenshot(path=path, full_page=full)
    print(f"  [ok] {name}.png")
    results.append(name)


def goto(page, url):
    page.goto(BASE + url, wait_until="load", timeout=45000)
    page.wait_for_timeout(500)


def login(page, email, password, admin=False):
    if admin:
        goto(page, "/secure-admin-panel/login/?next=/secure-admin-panel/")
        page.fill("input[name=username]", email)
        page.fill("input[name=password]", password)
        page.click("input[type=submit]")
    else:
        goto(page, "/accounts/login/")
        page.fill("input[name=email]", email)
        page.fill("input[name=password]", password)
        page.click("button:has-text('Iniciar')")
    page.wait_for_load_state("load")
    page.wait_for_timeout(800)


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
            locale="es-PY",
        )
        page = ctx.new_page()

        # ---------- PUBLIC PAGES ----------
        print("Capturing public pages...")
        goto(page, "/")
        shot(page, "01_home")

        goto(page, "/store/")
        shot(page, "02_store_all_products")

        goto(page, "/store/category/computadoras/")
        shot(page, "03_store_category_computadoras")

        goto(page, "/store/category/computadoras/macbook-pro/")
        shot(page, "04_product_detail_macbook")

        goto(page, "/store/search/?keyword=gamer")
        shot(page, "05_search_results")

        goto(page, "/cart/")
        shot(page, "06_cart_empty")

        goto(page, "/accounts/login/")
        shot(page, "07_login")

        goto(page, "/accounts/register/")
        shot(page, "08_register")

        goto(page, "/accounts/forgotPassword/")
        shot(page, "09_forgot_password")

        # ---------- AUTHENTICATED STOREFRONT ----------
        print("Logging in as demo user...")
        login(page, USER_EMAIL, PASSWORD)
        shot(page, "10_dashboard")

        goto(page, "/accounts/my_orders/")
        shot(page, "11_my_orders")

        goto(page, "/accounts/edit_profile/")
        shot(page, "12_edit_profile")

        goto(page, "/accounts/change_password/")
        shot(page, "13_change_password")

        # Add products to the cart
        print("Adding products to cart...")
        for pid in (5, 7, 1):  # Macbook, Mouse Gamer, Headphones
            goto(page, f"/cart/add_cart/{pid}/")
        goto(page, "/cart/")
        shot(page, "14_cart_with_items")

        # Checkout
        goto(page, "/cart/checkout/")
        shot(page, "15_checkout")

        # Fill billing details and place the order
        print("Placing order...")
        page.fill("input[name=first_name]", "Pepe")
        page.fill("input[name=last_name]", "Gonzalez")
        page.fill("input[name=email]", ORDER_EMAIL)
        page.fill("input[name=phone]", "+595 981 123 456")
        page.fill("input[name=address_line_1]", "Avda. Mariscal Lopez 1234")
        page.fill("input[name=address_line_2]", "Edificio Central, Piso 3")
        page.fill("input[name=city]", "Asuncion")
        page.fill("input[name=state]", "Central")
        page.fill("input[name=country]", "Paraguay")
        page.fill("textarea[name=order_note]", "Entregar en horario de oficina.")
        page.click("button:has-text('Pagar')")
        page.wait_for_load_state("load")
        page.wait_for_timeout(1500)
        shot(page, "16_payments_paypal")

        # Simulate the PayPal approval -> backend creates the order & emails it
        print("Simulating payment + sending confirmation email...")
        resp = page.evaluate(
            """async () => {
                function getCookie(name){
                    let v=null; const cs=document.cookie.split(';');
                    for(const c of cs){const t=c.trim();
                        if(t.startsWith(name+'=')){v=decodeURIComponent(t.slice(name.length+1));break;}}
                    return v;
                }
                const r = await fetch('/orders/payments/', {
                    method:'POST',
                    headers:{'Content-Type':'application/json','X-CSRFToken':getCookie('csrftoken')},
                    body: JSON.stringify({orderID:'DEMO-TXN-77231', transID:'DEMO-TXN-77231',
                        payment_method:'PayPal', status:'COMPLETED'})
                });
                return await r.json();
            }"""
        )
        print("  payment response:", resp)
        if isinstance(resp, dict) and resp.get("url"):
            goto(page, resp["url"])
        else:
            goto(page, "/orders/order_complete/")
        shot(page, "17_order_complete")

        ctx.close()

        # ---------- ADMIN PANEL ----------
        print("Capturing admin panel...")
        actx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
            locale="es-PY",
        )
        apage = actx.new_page()
        login(apage, ADMIN_EMAIL, PASSWORD, admin=True)
        shot(apage, "18_admin_dashboard")

        goto(apage, "/secure-admin-panel/store/product/")
        shot(apage, "19_admin_products")

        goto(apage, "/secure-admin-panel/orders/order/")
        shot(apage, "20_admin_orders")

        goto(apage, "/secure-admin-panel/accounts/account/")
        shot(apage, "21_admin_users")

        goto(apage, "/secure-admin-panel/orders/payment/")
        shot(apage, "22_admin_payments")

        actx.close()
        browser.close()

    print(f"\nDONE. {len(results)} screenshots saved to {OUT}")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("ERROR during capture:", repr(e))
        sys.exit(1)
