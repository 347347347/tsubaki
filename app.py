"""
tsubaki - クラウドソーシング自動化ダッシュボード
Flask Webアプリ本体
"""

from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

# ==============================
# ルーティング
# ==============================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/fetch-jobs", methods=["POST"])
def fetch_jobs():
    """RSS取得＋フィルタリング"""
    try:
        from rss_filter import fetch_new_jobs
        jobs = fetch_new_jobs()
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
