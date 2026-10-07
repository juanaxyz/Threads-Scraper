import asyncio
import csv

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from app.browser.browser import start_browser
from app.config import (
    FIELDS,
    IDLE_BEFORE_HINT,
    IDLE_FINAL_PAUSE_MS,
    IDLE_PAUSE_MS,
    OUTPUT_FILE,
    POST_SELECTOR,
    SCROLL_GROWTH_TIMEOUT_MS,
    SCROLL_WAIT_MS,
    SEARCH_URL,
)
from app.scraper.parser import extract_posts


async def wait_for_enter(stop_event):
    await asyncio.to_thread(input, ">>> Tekan ENTER kapan saja untuk berhenti...\n")
    stop_event.set()


async def scroll_and_collect(page, posts, writer, csv_file, stop_event):
    seen = set()
    total = 0
    idle = 0

    new_items = await extract_posts(posts, seen)
    writer.writerows(new_items)
    csv_file.flush()
    total += len(new_items)
    print(f"First load: {total} post")

    while not stop_event.is_set():
        prev_height = await page.evaluate("document.body.scrollHeight")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        try:
            await page.wait_for_function(
                "(h) => document.body.scrollHeight > h",
                arg=prev_height,
                timeout=SCROLL_GROWTH_TIMEOUT_MS,
            )
        except PlaywrightTimeoutError:
            pass

        await page.wait_for_timeout(SCROLL_WAIT_MS)

        new_items = await extract_posts(posts, seen)

        if new_items:
            writer.writerows(new_items)
            csv_file.flush()
            total += len(new_items)
            idle = 0
            print(f"Total: {total} post (+{len(new_items)})")
        else:
            idle += 1
            print(f"Tidak ada post baru (x{idle})")
            if idle == IDLE_BEFORE_HINT:
                print("Kemungkinan sudah data terakhir. Tekan ENTER kalau ingin selesai.")
            await page.wait_for_timeout(
                IDLE_PAUSE_MS if idle < IDLE_BEFORE_HINT else IDLE_FINAL_PAUSE_MS
            )

    return total


async def run():
    playwright, browser, context = await start_browser()

    try:
        page = await context.new_page()
        await page.goto(SEARCH_URL)

        posts = page.locator(POST_SELECTOR)
        await posts.first.wait_for(state="visible")

        stop_event = asyncio.Event()
        enter_task = asyncio.create_task(wait_for_enter(stop_event))

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            total = await scroll_and_collect(page, posts, writer, f, stop_event)

        await enter_task
        print(f"Selesai. {total} post tersimpan di {OUTPUT_FILE}")

    finally:
        await context.close()
        await browser.close()
        await playwright.stop()


if __name__ == "__main__":
    asyncio.run(run())
