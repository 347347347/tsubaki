"""
AI提案文生成ツール（Google Gemini API使用・無料枠対応）
使い方: python propose.py

必要ライブラリ: pip install google-generativeai
環境変数:      export GEMINI_API_KEY="AIzaSyAufdo7-huRcNoRWmdXMqWQOm_Z6_66wNo"
"""

import google.generativeai as genai
import os

# ==============================
# あなたのプロフィール設定
# ==============================

PROFILE = """
- 経験年数: Web制作3年以上
- 得意スキル: WordPressカスタマイズ、LP・コーポレートサイト制作、HTML/CSSコーディング、JavaScript / jQuery
- 対応可能な案件: WordPress構築・カスタマイズ、LP制作、コーポレートサイト制作、レスポンシブ対応コーディング
- 強み: 納期厳守、丁寧なコミュニケーション、修正対応が迅速
- トーン: 丁寧・誠実
"""

# ==============================
# プロンプト
# ==============================

SYSTEM_PROMPT = f"""
あなたはクラウドソーシングの提案文作成の専門家です。
以下のフリーランサーのプロフィールをもとに、案件に対する提案文を作成してください。

【フリーランサープロフィール】
{PROFILE}

【提案文のルール】
- 文字数: 300〜400字程度
- 構成: ①挨拶・応募意思 → ②自己紹介・実績 → ③案件への具体的な対応方針 → ④締め
- トーン: 丁寧・誠実。押しつけがましくなく、頼みやすい印象
- 「〜させていただきます」の多用は避ける
- テンプレート感が出ないよう、案件の内容に合わせて具体的に書く
- 最後に【ポイント解説】として提案文の工夫した点を2〜3行で添える
"""

# ==============================
# Geminiクライアントの初期化
# ==============================

def get_model():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("[エラー] GEMINI_API_KEY が設定されていません\n"
                         "export GEMINI_API_KEY='AIzaSy...' を実行してください")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT
    )

# ==============================
# 提案文生成
# ==============================

def generate_proposal(job_title: str, job_description: str) -> str:
    """案件タイトルと概要から提案文を生成する"""
    try:
        model = get_model()
        prompt = f"""
以下の案件に対する提案文を作成してください。

【案件タイトル】
{job_title}

【案件概要】
{job_description}
"""
        response = model.generate_content(prompt)
        return response.text

    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"[エラー] 生成に失敗しました: {e}"

# ==============================
# インタラクティブモード
# ==============================

def interactive_mode():
    print("\n" + "="*60)
    print("  AI提案文生成ツール（Gemini）")
    print("="*60)
    print("案件情報を入力してください（終了: Ctrl+C）\n")

    while True:
        try:
            print("-" * 40)
            title = input("案件タイトル: ").strip()
            if not title:
                print("タイトルを入力してください")
                continue

            print("案件概要（入力後Enterを2回押す）:")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            description = "\n".join(lines)

            print("\n⏳ 提案文を生成中...\n")
            result = generate_proposal(title, description)

            print("="*60)
            print(result)
            print("="*60)

            again = input("\n別の案件を生成しますか？ [y/N]: ").strip().lower()
            if again != "y":
                break

        except KeyboardInterrupt:
            print("\n終了します")
            break

# ==============================
# rss_filter.py と連携するモード
# ==============================

def batch_mode(jobs: list[dict]) -> list[dict]:
    """
    rss_filter.pyのfetch_new_jobs()と組み合わせて使う。
    各案件に提案文を追加して返す。
    """
    results = []
    for job in jobs:
        print(f"[生成中] {job['title'][:40]}...")
        proposal = generate_proposal(job["title"], job["summary"])
        results.append({**job, "proposal": proposal})
    return results

# ==============================
# メイン
# ==============================

if __name__ == "__main__":
    interactive_mode()
