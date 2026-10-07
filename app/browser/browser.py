from playwright.async_api import async_playwright

from app.config import SESSION_FILE, HEADLESS

# Tipe resource yang diblokir. Yang dipakai hanya data teks (HTML + XHR/JS), jadi aman.
BLOCKED_RESOURCE_TYPES = {"image", "media", "font"}   # tambahkan "stylesheet" jika berani, lihat catatan

# Domain tracking/analytics (opsional)
BLOCKED_URL_KEYWORDS = (
    "google-analytics.com",
    "googletagmanager.com",
    "doubleclick.net",
    "/ajax/bz",          # beacon telemetri Meta
    "/logging/",
)


async def block_unneeded(route):
    request = route.request
    if request.resource_type in BLOCKED_RESOURCE_TYPES:
        await route.abort()
    elif any(k in request.url for k in BLOCKED_URL_KEYWORDS):
        await route.abort()
    else:
        await route.continue_()

async def start_browser():

    playwright = await async_playwright().start()

    browser = await playwright.firefox.launch(
        headless=HEADLESS
    )

    if not SESSION_FILE.exists():
        print(
            "File session belum ada. "
            "Silakan jalankan modul auth terlebih dahulu."
        )

        context = await browser.new_context()

    else:
        context = await browser.new_context(
            storage_state=SESSION_FILE
        )
        await context.route("**/*", block_unneeded)

    return playwright, browser, context