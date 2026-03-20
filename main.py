"""
クラウドソーシング案件 自動通知 — メインスクリプト
使い方: python main.py

必要ライブラリ: pip install feedparser requests
環境変数:      export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1484465985678479462/-fJiyZn4HQzf4-QdM5pOm6MrcDePUdS4hys_LHFNmkmMnEYo9IN41GGskWzboaJmNgzw"
"""

from rss_filter import fetch_new_jobs, print_jobs
from notify_discord import notify_discord, notify_summary
from datetime import datetime

if __name__ == "__main__":
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 案件チェック開始")

    # 1. RSS取得＋フィルタリング
    jobs = fetch_new_jobs()

    # 2. ターミナルに表示
    print_jobs(jobs)

    # 3. Discordに通知
    #    件数が多い場合はサマリーだけ → 各案件の詳細通知
    notify_summary(jobs)
    notify_discord(jobs)

    print(f"[完了] {len(jobs)} 件を通知しました\n")
