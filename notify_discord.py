"""
Discord Webhook 通知モジュール
rss_filter.py と組み合わせて使う
"""

import requests
import os

# ==============================
# 設定
# ==============================

# 環境変数から読み込む（.envファイルまたはexportで設定）
# export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1484465985678479462/-fJiyZn4HQzf4-QdM5pOm6MrcDePUdS4hys_LHFNmkmMnEYo9IN41GGskWzboaJmNgzw"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")


def notify_discord(jobs: list[dict]) -> None:
    """新着案件リストをDiscordに通知する"""

    if not jobs:
        return

    if not DISCORD_WEBHOOK_URL:
        print("[警告] DISCORD_WEBHOOK_URL が設定されていません")
        return

    for job in jobs:
        # Discordのリッチ埋め込みメッセージ（Embed）形式
        embed = {
            "title": job["title"][:256],  # Discordのタイトル上限
            "url": job["url"],
            "color": 0x5865F2,  # Discord紫
            "fields": [
                {
                    "name": "💰 単価",
                    "value": job["price"],
                    "inline": True
                },
                {
                    "name": "📋 媒体",
                    "value": job["source"],
                    "inline": True
                },
                {
                    "name": "📝 概要",
                    "value": job["summary"][:200] if job["summary"] else "（概要なし）",
                    "inline": False
                },
            ],
            "footer": {
                "text": f"投稿日: {job['date'][:16] if job['date'] else '不明'}"
            }
        }

        payload = {
            "username": "案件通知Bot",
            "embeds": [embed]
        }

        try:
            resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
            resp.raise_for_status()
            print(f"[通知済み] {job['title'][:40]}...")
        except requests.RequestException as e:
            print(f"[通知エラー] {e}")


def notify_summary(jobs: list[dict]) -> None:
    """件数サマリーだけを通知する（まとめ通知）"""

    if not DISCORD_WEBHOOK_URL:
        return

    if not jobs:
        message = "✅ 新着案件チェック完了 — 新しい案件はありませんでした"
    else:
        titles = "\n".join(f"• {j['title'][:50]}" for j in jobs[:5])
        more = f"\n…他{len(jobs)-5}件" if len(jobs) > 5 else ""
        message = f"🔔 **新着案件 {len(jobs)} 件**\n{titles}{more}"

    payload = {
        "username": "案件通知Bot",
        "content": message
    }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except requests.RequestException as e:
        print(f"[サマリー通知エラー] {e}")
