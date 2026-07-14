"""Shine.com profile updater.

Strategy: login → open profile → toggle a trivial field (edit & re-save) → logout.
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

log = logging.getLogger("updater.shine")

LOGIN_URL = "https://www.shine.com/myshine/login"
PROFILE_URL = "https://www.shine.com/myshine/my-profile"


async def update() -> bool:
    creds = get_creds("SHINE")
    if not creds:
        log.info("Shine: no creds, skipping")
        return False
    email, password = creds

    async with browser_session() as page:
        log.info("Shine: opening login")
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        await human_delay()

        try:
            await type_like_human(page, 'input[name="email"], input[type="email"]', email)
            await human_delay()
            await type_like_human(page, 'input[name="password"], input[type="password"]', password)
            await human_delay()
            await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")')
        except PWTimeout:
            await save_screenshot(page, "shine_login_fail")
            return False

        try:
            await page.wait_for_url("**/myshine/**", timeout=30000)
        except PWTimeout:
            await save_screenshot(page, "shine_login_timeout")
            return False

        log.info("Shine: logged in, going to profile")
        await page.goto(PROFILE_URL, wait_until="domcontentloaded")
        await human_delay(2, 4)

        # Try to open "Profile Summary" or "Headline" edit
        edit_triggered = False
        for text_sel in ["Profile Summary", "Summary", "Headline", "Career Summary"]:
            try:
                section = page.get_by_text(text_sel, exact=False).first
                await section.scroll_into_view_if_needed(timeout=3000)
                # Find a nearby edit/pencil button
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
                log.info("Shine: summary re-saved")
                await human_delay(2, 3)
            except Exception as e:
                log.warning("Shine: save failed: %s", e)

        # Try "Update Profile" / "Refresh" button if available
        for btn_text in ["Update Profile", "Refresh Profile", "Update"]:
            try:
                await page.get_by_role("button", name=btn_text).first.click(timeout=2000)
                await human_delay(2, 3)
                log.info("Shine: clicked '%s'", btn_text)
                break
            except Exception:
                continue

        await save_screenshot(page, "shine_done")
        log.info("Shine: update complete")
        return True
