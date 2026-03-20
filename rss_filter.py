"""
クラウドソーシング案件 RSS取得＋フィルタリング
対象: クラウドワークス / ランサーズ
条件: Web制作・WordPress / 1万3千円以上
"""

import feedparser
import json
import os
import re
from datetime import datetime

# ==============================
# 設定（ここを自分好みに変更）
# ==============================

# 検索キーワード（タイトル・説明文に含まれていればヒット）
KEYWORDS = [
    "Web制作", "ウェブ制作", "WordPress", "ワードプレス",
    "LP制作", "ランディングページ", "ホームページ制作", "サイト制作",
    "HTML", "CSS", "コーディング"
]

# 最低単価（円）
MIN_PRICE = 13000

# RSSフィードURL
RSS_FEEDS = {
    "クラウドワークス_Web": "https://crowdworks.jp/public/jobs/search.atom?category_id=1&order=new",
    "クラウドワークス_IT": "https://crowdworks.jp/public/jobs/search.atom?category_id=2&order=new",
    "ランサーズ_Web": "https://www.lancers.jp/feed/search/task?keyword=Web%E5%88%B6%E4%BD%9C&sort=new",
    "ランサーズ_WP": "https://www.lancers.jp/feed/search/task?keyword=WordPress&sort=new",
}

# 通知済み案件を保存するファイル（重複通知防止）
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
    """
    テキストから金額を抽出して整数で返す。
    例: "15,000円" -> 15000 / "3万円" -> 30000
    見つからない場合は 0 を返す。
    """
    # "〇万〇千円" パターン
    m = re.search(r'(\d+)万(\d+)?[千]?円', text)
    if m:
        man = int(m.group(1)) * 10000
        sen = int(m.group(2)) * 1000 if m.group(2) else 0
        return man + sen

    # "〇万円" パターン
    m = re.search(r'(\d+)万円', text)
    if m:
        return int(m.group(1)) * 10000

    # カンマ区切り数字 "15,000" パターン
    m = re.search(r'(\d{1,3}(?:,\d{3})+)', text)
    if m:
        return int(m.group(1).replace(",", ""))

    # 普通の数字（4桁以上）
    m = re.search(r'(\d{4,})', text)
    if m:
        return int(m.group(1))

    return 0

# ==============================
# フィルタリング
# ==============================

def matches_keywords(entry) -> bool:
    """タイトルまたは概要にキーワードが含まれているか"""
    text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    return any(kw.lower() in text for kw in KEYWORDS)

def matches_price(entry) -> bool:
    """
    単価が最低ラインを満たすか。
    RSSに金額情報がない場合は True（見逃さないよう通過させる）
    """
    text = entry.get("title", "") + " " + entry.get("summary", "")
    price = extract_price(text)
    if price == 0:
        return True  # 金額不明は通過（詳細ページで確認）
    return price >= MIN_PRICE

# ==============================
# RSS取得＋フィルタリング
# ==============================

def fetch_new_jobs() -> list[dict]:
    seen = load_seen()
    new_jobs = []

    for source_name, url in RSS_FEEDS.items():
        print(f"[取得中] {source_name} ...")
        feed = feedparser.parse(url)

        for entry in feed.entries:
            job_id = entry.get("id") or entry.get("link", "")

            # 通知済みはスキップ
            if job_id in seen:
                continue

            # フィルタリング
            if not matches_keywords(entry):
                continue
            if not matches_price(entry):
                continue

            # 単価を取得（表示用）
            text = entry.get("title", "") + " " + entry.get("summary", "")
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
    print(f"フィルター: {', '.join(KEYWORDS[:4])}... / {MIN_PRICE:,}円以上")

    jobs = fetch_new_jobs()
    print_jobs(jobs)

    # 次のステップ: LINE通知を追加する場合はここで notify_line(jobs) を呼ぶ
    # from line_notify import notify_line
    # notify_line(jobs)
