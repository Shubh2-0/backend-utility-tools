"""Naukri profile updater.

Strategy:
 1. Login via naukri.com/nlogin/login
 2. Navigate to profile page
 3. Open Resume Headline edit, re-save without changing content
    (this updates the `lastModified` timestamp, pushing profile up in recruiter search).
 4. Logout.

Naukri is relatively automation-tolerant for benign profile updates.
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

log = logging.getLogger("updater.naukri")

LOGIN_URL = "https://www.naukri.com/nlogin/login"
PROFILE_URL = "https://www.naukri.com/mnjuser/profile"


async def update() -> bool:
    creds = get_creds("NAUKRI")
    if not creds:
        log.info("Naukri: no creds, skipping")
        return False
    email, password = creds

    async with browser_session() as page:
        log.info("Naukri: opening login")
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        await human_delay()

        try:
            await type_like_human(page, 'input[placeholder*="Email" i]', email)
            await human_delay()
            await type_like_human(page, 'input[placeholder*="password" i]', password)
            await human_delay()
            await page.click('button[type="submit"]')
        except PWTimeout:
            await save_screenshot(page, "naukri_login_fail")
            log.error("Naukri: login form not found")
            return False

        # Wait for dashboard
        try:
            await page.wait_for_url("**/mnjuser/**", timeout=30000)
        except PWTimeout:
            await save_screenshot(page, "naukri_login_timeout")
            log.error("Naukri: login did not redirect")
            return False

        log.info("Naukri: logged in, going to profile")
        await page.goto(PROFILE_URL, wait_until="domcontentloaded")
        await human_delay(2, 4)

        # Trigger an "edit then save" on Resume Headline
        # Naukri's profile page has edit pencil icons with class containing "edit"
        updated = False
        for selector in [
            'span.edit.icon:near(:text("Resume headline"))',
            'span:has-text("Resume headline") ~ * span.edit',
            'div:has-text("Resume headline") span.edit',
            '[data-ga-track*="resume_headline" i] span.edit',
        ]:
            try:
                await page.locator(selector).first.click(timeout=4000)
                updated = True
                break
            except Exception:
                continue

        if not updated:
            # Fallback: scroll and try finding any visible edit icon on headline section
            try:
                await page.get_by_text("Resume headline", exact=False).first.scroll_into_view_if_needed()
                await human_delay()
                await page.locator('text=Resume headline').locator("..").locator("span.edit").first.click(timeout=4000)
                updated = True
            except Exception as e:
                log.warning("Naukri: could not click edit icon: %s", e)

        if updated:
            await human_delay(1, 2)
            # Tweak the headline: add a trailing space then remove it, press Save
            try:
                textarea = page.locator('textarea').first
                current = await textarea.input_value()
                await textarea.fill(current + " ")
                await human_delay(0.5, 1)
                await textarea.fill(current.strip())
                await human_delay()
                await page.get_by_role("button", name="Save").click(timeout=5000)
                log.info("Naukri: headline re-saved")
                await human_delay(2, 4)
            except Exception as e:
                log.warning("Naukri: save step failed: %s", e)
                await save_screenshot(page, "naukri_save_fail")

        # Also click "Update" button if present (Naukri shows one on top of profile)
        try:
            await page.get_by_role("button", name="Update").first.click(timeout=3000)
            await human_delay(2, 3)
            log.info("Naukri: clicked Update button")
        except Exception:
            pass

        await save_screenshot(page, "naukri_done")
        log.info("Naukri: update complete")
        return True
