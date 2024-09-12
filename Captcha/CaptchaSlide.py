import json
import os
import random

from playwright.sync_api import sync_playwright
from retry import retry


def passSlideCaptcha():
    browser = getBrowser()
    result = solve(browser)
    return result


def solve(browser):
    page = browser.new_page()
    page.goto("file:///" + os.path.abspath('slide.html'))

    slide_btn = page.query_selector(".btn_slide")
    slide_scale = page.query_selector(".nc_scale")

    btn_box = slide_btn.bounding_box()
    width = slide_scale.bounding_box()['width'] + btn_box['width']

    offsets = []
    while width > 0:
        offset = min(random.randint(50, 70), width)
        width -= offset
        offsets.append(offset)

    x = btn_box['x'] + btn_box['width'] / 2
    y = btn_box['y'] + btn_box['height'] / 2

    page.mouse.move(x, y)
    page.mouse.down()
    for offset in offsets:
        page.mouse.move(x, y)
        x += offset
    page.mouse.up()

    @retry()
    def get_result():
        return page.query_selector("#mync").inner_html()
    ret = json.loads(get_result())
    page.close()
    return ret


def getBrowser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True, channel="msedge")
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 "
                   "Safari/537.36 Edg/126.0.0.0"
    )
    context.add_init_script(script='Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
    return context
