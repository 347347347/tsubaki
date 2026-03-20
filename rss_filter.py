"""
クラウドソーシング案件 RSS取得＋フィルタリング
対象: クラウドワークス / ランサーズ
"""

import feedparser
import json
import os
import re
from datetime import datetime

# ==============================
# デフォルト設定
# ==============================

DEFAULT_KEYWORDS = [
    "Web制作", "ウェブ制作", "WordPress", "ワードプレス",
    "LP制作", "ランディングページ", "ホームページ制作", "サイト制作",
    "HTML", "CSS", "コーディング"
]

DEFAULT_MIN_PRICE = 13000

RSS_FEEDS = {
    "クラウドワークス_Web": "https://crowdworks.jp/public/jobs/search.atom?category_id=1&order=new",
    "クラウドワークス_IT":  "https://crowdworks.jp/public/jobs/search.atom?category_id=2&order=new",
    "ランサーズ_Web":       "https://www.lancers.jp/feed/search/task?keyword=Web%E5%88%B6%E4%BD%9C&sort=new",
    "ランサーズ_WP":        "https://www.lancers.jp/feed/search/task?keyword=WordPress&sort=new",
}

SEEN_FILE = "seen_jobs.json"

# ==============================
# 通知済みIDの読み書き
# ==============================

def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_seen(seen: set):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False)

# ==============================
# 単価の抽出
# ==============================

def extract_price(text: str) -> int:
    m = re.search(r'(\d+)万(\d+)?[千]?円', text)
    if m:
        man = int(m.group(1)) * 10000
        sen = int(m.group(2)) * 1000 if m.group(2) else 0
        return man + sen
    m = re.search(r'(\d+)万円', text)
    if m:
        return int(m.group(1)) * 10000
    m = re.search(r'(\d{1,3}(?:,\d{3})+)', text)
    if m:
        return int(m.group(1).replace(",", ""))
    m = re.search(r'(\d{4,})', text)
    if m:
        return int(m.group(1))
    return 0

# ==============================
# フィルタリング
# ==============================

def matches_keywords(entry, keywords: list) -> bool:
    text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    return any(kw.lower() in text for kw in keywords)

def matches_price(entry, min_price: int) -> bool:
    text = entry.get("title", "") + " " + entry.get("summary", "")
    price = extract_price(text)
    if price == 0:
        return True  # 金額不明は通過
    return price >= min_price

# ==============================
# RSS取得＋フィルタリング
# ==============================

def fetch_new_jobs(
    keywords: list = None,
    min_price: int = None
) -> list[dict]:
    """
    keywords, min_price を外から渡せるようにした。
    省略時はデフォルト値を使う。
    """
    if keywords is None:
        keywords = DEFAULT_KEYWORDS
    if min_price is None:
        min_price = DEFAULT_MIN_PRICE

    seen = load_seen()
    new_jobs = []

    for source_name, url in RSS_FEEDS.items():
        print(f"[取得中] {source_name} ...")
        feed = feedparser.parse(url)

        for entry in feed.entries:
            job_id = entry.get("id") or entry.get("link", "")

            if job_id in seen:
                continue
            if not matches_keywords(entry, keywords):
                continue
            if not matches_price(entry, min_price):
                continue

            text  = entry.get("title", "") + " " + entry.get("summary", "")
            price = extract_price(text)

            job = {
                "id":      job_id,
                "source":  source_name,
                "title":   entry.get("title", "（タイトルなし）"),
                "url":     entry.get("link", ""),
                "price":   f"{price:,}円" if price > 0 else "金額不明",
                "summary": entry.get("summary", "")[:120] + "...",
                "date":    entry.get("published", ""),
            }
            new_jobs.append(job)
            seen.add(job_id)

    save_seen(seen)
    return new_jobs

# ==============================
# 結果の表示
# ==============================

def print_jobs(jobs: list[dict]):
    if not jobs:
        print("\n新着案件はありませんでした。")
        return
    print(f"\n{'='*60}")
    print(f"  新着案件 {len(jobs)} 件")
    print(f"{'='*60}")
    for i, job in enumerate(jobs, 1):
        print(f"\n[{i}] {job['title']}")
        print(f"    媒体  : {job['source']}")
        print(f"    単価  : {job['price']}")
        print(f"    URL   : {job['url']}")
        print(f"    概要  : {job['summary']}")

# ==============================
# メイン
# ==============================

if __name__ == "__main__":
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    jobs = fetch_new_jobs()
    print_jobs(jobs)
