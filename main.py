import time
import hashlib
import requests
from datetime import datetime
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PROJECT_URL = "https://experts.afterquery.com/projects/rewrite"
CHECK_INTERVAL_SEC = 30

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def log(msg):
    print("[" + datetime.now().strftime("%H:%M:%S") + "] " + msg)

def send_telegram(message):
    try:
        url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        if r.ok:
            log("Telegram alert sent!")
        else:
            log("Telegram error: " + str(r.status_code))
    except Exception as e:
        log("Telegram exception: " + str(e))

def get_page_snapshot():
    try:
        r = requests.get(PROJECT_URL, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            page_hash = hashlib.md5(r.text.encode()).hexdigest()
            return page_hash, len(r.text)
        else:
            log("Status " + str(r.status_code))
            return None, 0
    except Exception as e:
        log("Fetch error: " + str(e))
        return None, 0

def main():
    log("AfterQuery Monitor starting on Railway!")
    send_telegram("AfterQuery Monitor Started!\nWatching Rewrite project\nLink: " + PROJECT_URL + "\nChecking every 30 seconds!")

    last_hash = None
    last_len = None

    while True:
        try:
            page_hash, page_len = get_page_snapshot()
            if page_hash is None:
                log("Could not reach page. Retrying...")
            else:
                log("Page size: " + str(page_len) + " | Hash: " + page_hash[:8])
                if last_hash is None:
                    log("Baseline set.")
                elif page_hash != last_hash:
                    size_diff = page_len - last_len
                    if size_diff == 0:
                        log("Hash changed but size same - ignored.")
                    else:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        log("PAGE CHANGED! Size diff: " + str(size_diff))
                        send_telegram("AfterQuery Rewrite - Page Changed!\nSize diff: " + str(size_diff) + " chars\nTime: " + now + "\nLink: " + PROJECT_URL + "\nCheck now - task may be available!")
                else:
                    log("No change.")
                last_hash = page_hash
                last_len = page_len
        except Exception as e:
            log("Unexpected error: " + str(e))
        time.sleep(CHECK_INTERVAL_SEC)

main()
