import re
from datetime import datetime

from app.config import TIMEZONE

# Baris awal "Replying to @user" (atau "Membalas @user" kalau tampilan Threads berbahasa Indonesia)
REPLY_PREFIX = re.compile(r"^\s*(Replying to|Membalas)\b[^\n]*\n?", re.IGNORECASE)

# Ekstraksi data post dari DOM search result Threads
EXTRACT_JS = r"""
    els => els.map(el => {
        // Akun: link /@username yang bukan link post
        const userA = [...el.querySelectorAll('a[href^="/@"]')]
            .find(a => !a.getAttribute('href').includes('/post/'));
        const akun = userA
            ? userA.getAttribute('href').replace('/@', '').split('/')[0]
            : "";

        // URL post & waktu
        const postA = el.querySelector('a[href*="/post/"]');
        const timeEl = el.querySelector('time');

        // Kategori (tag)
        const tagA = el.querySelector('a[href*="serp_type=tags"]');

        // Isi: span[dir=auto] terluar yang bukan bagian dari link/tombol/waktu
        const spans = [...el.querySelectorAll('span[dir="auto"]')].filter(s =>
            !s.closest('a, [role="button"]') &&
            !s.querySelector('time') &&
            !s.parentElement.closest('span[dir="auto"]')
        );
        const parts = spans.map(s => {
            const c = s.cloneNode(true);
            // buang penghitung "1/7" (berupa <div>) dari dalam teks
            c.querySelectorAll('div').forEach(d => d.remove());
            return c.textContent.replace(/\u00a0/g, ' ').trim();
        }).filter(Boolean);

        return {
            datetime: timeEl ? timeEl.getAttribute('datetime') : "",
            akun: akun,
            kategori: tagA ? tagA.textContent.trim() : "",
            isi: parts.join("\n"),
            url: postA ? postA.href : "",
        };
    })
"""


def bersihkan_isi(teks):
    return REPLY_PREFIX.sub("", teks, count=1).strip()


def format_tanggal(iso_str):
    """'2026-10-07T08:45:10.000Z' -> '2026/10/07' (zona waktu lokal)."""
    if not iso_str:
        return ""
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.astimezone(TIMEZONE).strftime("%Y/%m/%d")


def normalisasi(raw):
    """Ubah hasil ekstraksi DOM menjadi baris CSV, lewati yang kosong."""
    key = raw["url"] or (raw["akun"] + raw["isi"])
    if not key:
        return None, None
    return key, {
        "tanggal": format_tanggal(raw["datetime"]),
        "akun": raw["akun"],
        "kategori": raw["kategori"],
        "isi": bersihkan_isi(raw["isi"]),
        "url": raw["url"],
    }


async def extract_posts(posts, seen):
    """Ambil semua post yang ada di DOM saat ini, return hanya yang baru."""
    raw_items = await posts.evaluate_all(EXTRACT_JS)

    new_items = []
    for raw in raw_items:
        key, item = normalisasi(raw)
        if key is None or key in seen:
            continue
        seen.add(key)
        new_items.append(item)
    return new_items
