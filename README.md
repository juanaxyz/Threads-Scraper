# threads-scraper

Scraping hasil pencarian [Threads](https://www.threads.com) (misal kata kunci `ihsg`) dengan Playwright, lalu menyimpannya ke CSV. Berjalan otomatis sambil scroll, berhenti saat kamu tekan ENTER.

## Fitur

- Login sekali, session disimpan ke `session/threads_login.json` dan dipakai ulang
- Auto-scroll dan ekstrak post baru (dedup berdasarkan URL post)
- Blokir resource yang tidak perlu (image/media/font/tracking) supaya lebih ringan
- Cleanup teks: buang baris "Replying to @user" / "Membalas @user"
- Waktu ditampilkan sesuai jam Threads (WITA / Asia/Makassar)
- CSV ditulis langsung per batch (`data/threads_ihsg.csv`), aman kalau dihentikan sewaktu-waktu

## Persyaratan

- Python 3.9+ (dipakai `zoneinfo`)
- Browser Firefox untuk Playwright

```bash
pip install playwright
playwright install firefox
```

## Cara Pakai

**1. Login (sekali saja)**

```bash
python -m app.browser.auth
```

Browser Firefox akan terbuka → login manual di Threads → tekan ENTER. Session tersimpan di `session/threads_login.json`.

**2. Jalankan scraping**

```bash
python main.py
```

- Hasil disimpan ke `data/threads_ihsg.csv` (encoding `utf-8-sig`, aman dibuka di Excel)
- Tekan **ENTER** di terminal kapan saja untuk berhenti
- Kalau 3x scroll berturut-turut tidak ada post baru, kemungkinan sudah sampai data terakhir

## Struktur Project

```
threads-scraper/
├── main.py                  # entry point
├── app/
│   ├── config.py            # URL, selector, path, timezone, timing
│   ├── browser/
│   │   ├── auth.py          # simpan session login
│   │   └── browser.py       # start browser + blokir resource
│   └── scraper/
│       ├── parser.py        # ekstraksi DOM + bersihkan teks
│       └── search.py        # loop scroll & tulis CSV
├── data/                    # hasil CSV (di-ignore)
├── session/                 # session login (di-ignore)
└── .gitignore
```

## Konfigurasi

Semua pengaturan ada di [`app/config.py`](app/config.py):

| Konstanta | Fungsi |
| --- | --- |
| `QUERY` / `SEARCH_URL` | Kata kunci & URL pencarian |
| `OUTPUT_FILE` | Lokasi file CSV hasil |
| `FIELDS` | Kolom CSV |
| `POST_SELECTOR` | Selector elemen post di hasil pencarian |
| `SCROLL_WAIT_MS`, `IDLE_*` | Jeda scroll & deteksi akhir data |
| `TIMEZONE` | Zona waktu tampilan tanggal |

Ganti `QUERY` (atau `SEARCH_URL` langsung) untuk scraping kata kunci lain.

## Kolom CSV

| Kolom | Isi |
| --- | --- |
| `tanggal` | Tanggal post, format `YYYY/MM/DD` |
| `akun` | Username tanpa `@` |
| `kategori` | Tag/postingan kategori |
| `isi` | Isi post |
| `url` | URL lengkap post |

## Troubleshooting

- **`File session belum ada`** — jalankan `python -m app.browser.auth` dulu.
- **Selector tidak ketemu / 0 post** — struktur DOM Threads sering berubah; cek ulang `POST_SELECTOR` dan fungsi di `app/scraper/parser.py`.
- **Mau riset selector** — jalankan `python main.py`, lalu inspeksi elemen hasil pencarian di browser yang terbuka.

## Catatan

ini adalah project unofficial untuk mengambil data postingan dari threads, jika ada kendala dengan akun yang digunakan maka itu diluar tanggung jawab developer
