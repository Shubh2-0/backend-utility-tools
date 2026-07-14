"""Indeed profile updater.

NOTE: Indeed has stricter bot detection than Indian portals. If script fails
repeatedly, set INDEED_EMAIL/PASSWORD blank to skip it, and update Indeed
profile manually once a week.
"""
from __future__ import annotations

import logging

from playwright.async_api import TimeoutError as PWTimeout

from .base import (
    browser_session,
    get_creds,
    human_delay,
    save_screenshot,
    type_like_human,
)

log = logging.getLogger("updater.indeed")

LOGIN_URL = "https://secure.indeed.com/account/login"
PROFILE_URL = "https://profile.indeed.com/"


async def update() -> bool:
    creds = get_creds("INDEED")
    if not creds:
        log.info("Indeed: no creds, skipping")
        return False
    email, password = creds

    async with browser_session() as page:
        log.info("Indeed: opening login")
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        await human_delay(2, 4)

        try:
            await type_like_human(page, 'input[type="email"], input[name="__email"]', email)
            await human_delay()
            # Indeed sometimes splits login into two steps
            for btn_text in ["Continue", "Sign in"]:
                try:
                    await page.get_by_role("button", name=btn_text).first.click(timeout=2500)
                    break
                except Exception:
                    continue
            await human_delay(1.5, 3)
            await type_like_human(page, 'input[type="password"], input[name="__password"]', password)
            await human_delay()
            await page.get_by_role("button", name="Sign in").first.click(timeout=5000)
        except PWTimeout:
            await save_screenshot(page, "indeed_login_fail")
            return False

        try:
            await page.wait_for_load_state("networkidle", timeout=30000)
        except PWTimeout:
            pass

        # Detect CAPTCHA / challenge
        content = (await page.content()).lower()
        if "captcha" in content or "verify" in content:
            log.warning("Indeed: CAPTCHA/verification triggered; skipping")
            await save_screenshot(page, "indeed_captcha")
            return False

        await page.goto(PROFILE_URL, wait_until="domcontentloaded")
        await human_delay(2, 4)

        # Edit-save cycle on headline
        edit_triggered = False
        for text_sel in ["Headline", "Summary", "About"]:
            try:
                section = page.get_by_text(text_sel, exact=False).first
                await section.scroll_into_view_if_needed(timeout=3000)
                await section.locator("xpath=ancestor::*[1]").locator(
                    'button, [aria-label*="edit" i]'
                ).first.click(timeout=3000)
                edit_triggered = True
                break
            except Exception:
                continue

        if edit_triggered:
            try:
                ta = page.locator('textarea, input[type="text"]').first
                current = await ta.input_value()
                await ta.fill(current + " ")
                await human_delay(0.5, 1)
                await ta.fill(current.strip())
                await human_delay()
                await page.get_by_role("button", name="Save").first.click(timeout=5000)
                log.info("Indeed: section re-saved")
                await human_delay(2, 3)
            except Exception as e:
                log.warning("Indeed: save failed: %s", e)

        await save_screenshot(page, "indeed_done")
        log.info("Indeed: update complete")
        return True
