"""
tsubaki - クラウドソーシング自動化ダッシュボード
Flask Webアプリ本体
"""

from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

# ==============================
# フィルター設定の読み書き
# ==============================

FILTER_FILE = "filter_settings.json"

DEFAULT_FILTER = {
    "keywords": [
        "Web制作", "ウェブ制作", "WordPress", "ワードプレス",
        "LP制作", "ランディングページ", "ホームページ制作", "サイト制作",
        "HTML", "CSS", "コーディング"
    ],
    "min_price": 13000
}

def load_filter() -> dict:
    if os.path.exists(FILTER_FILE):
        with open(FILTER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_FILTER.copy()

def save_filter(settings: dict):
    with open(FILTER_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

# ==============================
# ルーティング
# ==============================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/filter", methods=["GET"])
def get_filter():
    """現在のフィルター設定を返す"""
    return jsonify({"ok": True, "filter": load_filter()})


@app.route("/api/filter", methods=["POST"])
def set_filter():
    """フィルター設定を保存する"""
    try:
        data = request.get_json()
        keywords  = [k.strip() for k in data.get("keywords", []) if k.strip()]
        min_price = int(data.get("min_price", 0))
        if not keywords:
            return jsonify({"ok": False, "error": "キーワードを1つ以上入力してください"}), 400
        save_filter({"keywords": keywords, "min_price": min_price})
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/fetch-jobs", methods=["POST"])
def fetch_jobs():
    """RSS取得＋フィルタリング"""
    try:
        settings = load_filter()
        from rss_filter import fetch_new_jobs
        jobs = fetch_new_jobs(
            keywords=settings["keywords"],
            min_price=settings["min_price"]
        )
        return jsonify({"ok": True, "jobs": jobs})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/propose", methods=["POST"])
def propose():
    """AI提案文生成"""
    try:
        data = request.get_json()
        title = data.get("title", "")
        summary = data.get("summary", "")
        if not title:
            return jsonify({"ok": False, "error": "タイトルが必要です"}), 400

        from propose import generate_proposal
        text = generate_proposal(title, summary)
        return jsonify({"ok": True, "proposal": text})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/add-calendar", methods=["POST"])
def add_calendar():
    """Googleカレンダーに案件登録"""
    try:
        data = request.get_json()
        title    = data.get("title", "")
        deadline = data.get("deadline", "")
        price    = data.get("price", "")
        url      = data.get("url", "")
        notes    = data.get("notes", "")

        if not title or not deadline:
            return jsonify({"ok": False, "error": "タイトルと納期は必須です"}), 400

        from calendar_add import add_job_to_calendar
        event = add_job_to_calendar(
            title=title,
            deadline=deadline,
            price=price,
            url=url,
            notes=notes
        )
        return jsonify({"ok": True, "link": event.get("htmlLink", "")})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/notify-discord", methods=["POST"])
def notify():
    """Discordに手動通知"""
    try:
        data = request.get_json()
        jobs = data.get("jobs", [])
        from notify_discord import notify_discord
        notify_discord(jobs)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ==============================
# 起動
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
