"""Foundit (ex-Monster India) profile updater."""
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

log = logging.getLogger("updater.foundit")

LOGIN_URL = "https://www.foundit.in/seeker/login"
PROFILE_URL = "https://www.foundit.in/seeker/profile"


async def update() -> bool:
    creds = get_creds("FOUNDIT")
    if not creds:
        log.info("Foundit: no creds, skipping")
        return False
    email, password = creds

    async with browser_session() as page:
        log.info("Foundit: opening login")
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        await human_delay()

        try:
            await type_like_human(page, 'input[type="email"], input[name="email"]', email)
            await human_delay()
            await type_like_human(page, 'input[type="password"], input[name="password"]', password)
            await human_delay()
            await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")')
        except PWTimeout:
            await save_screenshot(page, "foundit_login_fail")
            return False

        try:
            await page.wait_for_load_state("networkidle", timeout=25000)
        except PWTimeout:
            pass

        log.info("Foundit: going to profile")
        await page.goto(PROFILE_URL, wait_until="domcontentloaded")
        await human_delay(2, 4)

        # Try edit-save cycle on About Me / Profile Summary
        edit_triggered = False
        for text_sel in ["About me", "Profile Summary", "Summary", "Cover Letter"]:
            try:
                section = page.get_by_text(text_sel, exact=False).first
                await section.scroll_into_view_if_needed(timeout=3000)
                await section.locator("xpath=ancestor::*[1]").locator(
                    'button, [class*="edit" i], [aria-label*="edit" i]'
                ).first.click(timeout=3000)
                edit_triggered = True
                break
            except Exception:
                continue

        if edit_triggered:
            try:
                ta = page.locator("textarea").first
                current = await ta.input_value()
                await ta.fill(current + " ")
                await human_delay(0.5, 1)
                await ta.fill(current.strip())
                await human_delay()
                await page.get_by_role("button", name="Save").first.click(timeout=5000)
                log.info("Foundit: section re-saved")
                await human_delay(2, 3)
            except Exception as e:
                log.warning("Foundit: save failed: %s", e)

        await save_screenshot(page, "foundit_done")
        log.info("Foundit: update complete")
        return True
