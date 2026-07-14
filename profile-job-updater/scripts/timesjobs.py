"""TimesJobs profile updater."""
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

log = logging.getLogger("updater.timesjobs")

LOGIN_URL = "https://www.timesjobs.com/candidate/login.html"
PROFILE_URL = "https://www.timesjobs.com/candidate/my-profile.html"


async def update() -> bool:
    creds = get_creds("TIMESJOBS")
    if not creds:
        log.info("TimesJobs: no creds, skipping")
        return False
    email, password = creds

    async with browser_session() as page:
        log.info("TimesJobs: opening login")
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        await human_delay()

        try:
            await type_like_human(page, 'input[name*="email" i], input[type="email"]', email)
            await human_delay()
            await type_like_human(page, 'input[name*="password" i], input[type="password"]', password)
            await human_delay()
            await page.click('button[type="submit"], input[type="submit"], button:has-text("Login")')
        except PWTimeout:
            await save_screenshot(page, "timesjobs_login_fail")
            return False

        try:
            await page.wait_for_load_state("networkidle", timeout=25000)
        except PWTimeout:
            pass

        log.info("TimesJobs: going to profile")
        await page.goto(PROFILE_URL, wait_until="domcontentloaded")
        await human_delay(2, 4)

        # Try "Update" / "Refresh" button
        updated = False
        for btn_text in ["Update Profile", "Refresh Profile", "Update Resume", "Update"]:
            try:
                await page.get_by_role("button", name=btn_text).first.click(timeout=2500)
                updated = True
                log.info("TimesJobs: clicked '%s'", btn_text)
                await human_delay(2, 3)
                break
            except Exception:
                continue

        if not updated:
            # Fallback: edit-save on summary
            for text_sel in ["Profile Summary", "Summary", "Career Summary"]:
                try:
                    section = page.get_by_text(text_sel, exact=False).first
                    await section.scroll_into_view_if_needed(timeout=3000)
                    await section.locator("xpath=ancestor::*[1]").locator(
                        'a, button, [class*="edit" i]'
                    ).first.click(timeout=3000)
                    await human_delay()
                    ta = page.locator("textarea").first
                    current = await ta.input_value()
                    await ta.fill(current + " ")
                    await human_delay(0.5, 1)
                    await ta.fill(current.strip())
                    await page.get_by_role("button", name="Save").first.click(timeout=5000)
                    log.info("TimesJobs: summary re-saved")
                    await human_delay(2, 3)
                    break
                except Exception:
                    continue

        await save_screenshot(page, "timesjobs_done")
        log.info("TimesJobs: update complete")
        return True
