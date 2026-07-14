"""Shared helpers for all portal updaters."""
from __future__ import annotations

import asyncio
import logging
import os
import random
from contextlib import asynccontextmanager
from pathlib import Path

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

log = logging.getLogger("updater")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]

SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def human_delay(min_s: float = 0.8, max_s: float = 2.5) -> None:
    await asyncio.sleep(random.uniform(min_s, max_s))


async def type_like_human(page: Page, selector: str, text: str) -> None:
    await page.click(selector)
    await human_delay(0.3, 0.7)
    for ch in text:
        await page.keyboard.type(ch, delay=random.randint(40, 140))


@asynccontextmanager
async def browser_session(headless: bool = True):
    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context: BrowserContext = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1366, "height": 768},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )
        # Hide webdriver flag
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = await context.new_page()
        try:
            yield page
        finally:
            await context.close()
            await browser.close()


async def save_screenshot(page: Page, name: str) -> None:
    try:
        path = SCREENSHOT_DIR / f"{name}.png"
        await page.screenshot(path=str(path), full_page=False)
        log.info("screenshot saved: %s", path)
    except Exception as e:
        log.warning("screenshot failed: %s", e)


def get_creds(prefix: str) -> tuple[str, str] | None:
    email = os.getenv(f"{prefix}_EMAIL", "").strip()
    pwd = os.getenv(f"{prefix}_PASSWORD", "").strip()
    if not email or not pwd:
        return None
    return email, pwd
