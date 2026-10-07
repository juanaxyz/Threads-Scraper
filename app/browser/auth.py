import asyncio

from playwright.async_api import async_playwright

from app.config import SESSION_FILE

AUTH_FILE = SESSION_FILE


async def save_login():

    AUTH_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    async with async_playwright() as p:

        browser = await p.firefox.launch(
            headless=False
        )

        context = await browser.new_context()

        page = await context.new_page()

        await page.goto("https://www.threads.com/")

        print("Silakan login secara manual di browser.")

        input("Tekan ENTER setelah login berhasil...")

        await context.storage_state(
            path=AUTH_FILE
        )

        print(f"Session disimpan ke {AUTH_FILE}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(save_login())