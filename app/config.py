from pathlib import Path
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Session login ---
SESSION_FILE = BASE_DIR / "session" / "threads_login.json"

# --- Hasil scraping ---
OUTPUT_FILE = BASE_DIR / "data" / "threads_ihsg.csv"
FIELDS = ["tanggal", "akun", "kategori", "isi", "url"]
HEADLESS=True
# --- Pencarian Threads ---
QUERY = "ihsg"
SEARCH_URL = f"https://www.threads.com/search?q={QUERY}&filter=recent"
POST_SELECTOR = '[data-pagelet^="threads_search_results_"]'

# --- Perilaku scroll ---
SCROLL_WAIT_MS = 1000        # jeda antar scroll
SCROLL_GROWTH_TIMEOUT_MS = 5000  # tunggu tinggi halaman bertambah
IDLE_PAUSE_MS = 2000         # jeda saat belum ada post baru
IDLE_FINAL_PAUSE_MS = 5000   # jeda setelah 3x idle berturut-turut
IDLE_BEFORE_HINT = 3

# --- Waktu ---
TIMEZONE = ZoneInfo("Asia/Makassar")  # WITA (UTC+8), sama dengan jam yang tampil di Threads
