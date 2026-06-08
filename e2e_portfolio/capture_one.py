"""Recapture a single screen. Usage: capture_one.py <path> <out_name>"""
import os
import sys

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8010")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")

url_path = sys.argv[1]
if not url_path.startswith("/"):
    url_path = "/" + url_path
name = sys.argv[2]

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(
        viewport={"width": 1440, "height": 900}, device_scale_factor=2, locale="es-PY"
    )
    page = ctx.new_page()
    page.goto(BASE + url_path, wait_until="load", timeout=45000)
    page.wait_for_timeout(900)
    page.screenshot(path=os.path.join(OUT, name + ".png"), full_page=True)
    browser.close()
print("saved", name)
