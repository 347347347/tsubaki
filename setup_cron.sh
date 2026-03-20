#!/bin/bash
# ==============================
# cron 自動設定スクリプト
# 使い方: bash setup_cron.sh
# ==============================

PYTHON="/Users/mishinakenta/anaconda3/bin/python3"
APP_DIR="/Users/mishinakenta/Desktop/app/tsubaki"
LOG_FILE="$APP_DIR/cron.log"

# 追加するcronジョブ（30分おきに実行）
CRON_JOB="*/30 * * * * cd $APP_DIR && $PYTHON main.py >> $LOG_FILE 2>&1"

# すでに登録済みか確認
if crontab -l 2>/dev/null | grep -q "tsubaki"; then
    echo "[スキップ] すでにcronに登録されています"
    echo ""
    echo "現在の設定:"
    crontab -l | grep tsubaki
else
    # 既存のcronに追記
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "[完了] cronに登録しました"
    echo ""
    echo "登録内容:"
    crontab -l | grep tsubaki
fi

echo ""
echo "ログファイル: $LOG_FILE"
echo "動作確認:    tail -f $LOG_FILE"
