from flask import Flask, request, abort
import requests
import os
import openai

app = Flask(__name__)

# 環境変数
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# LINE返信用関数
def reply_message(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }
    requests.post(url, headers=headers, json=data)

# Webhook
@app.route("/webhook", methods=['POST'])
def webhook():
    body = request.json

    try:
        event = body['events'][0]
        reply_token = event['replyToken']

        # テキストメッセージ取得
        if event['message']['type'] == 'text':
            user_message = event['message']['text']
        else:
            reply_message(reply_token, "テキストを送ってください🙏")
            return 'OK'

    except:
        return 'OK'

    # GPTに投げる
    prompt = f"""
あなたはメルカリ販売のプロです。
以下の商品情報から売れる出品内容を作ってください。

【出力形式】
① タイトル
② 説明文
③ 推奨価格

商品情報：
{user_message}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        reply_text = response['choices'][0]['message']['content']

    except Exception as e:
        reply_text = "エラーが発生しました。もう一度試してください。"

    # LINEに返信
    reply_message(reply_token, reply_text)

    return 'OK'

# Render対応（超重要）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
