from flask import Flask, request, abort
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/webhook", methods=['POST'])
def webhook():
    body = request.json

    try:
        user_message = body['events'][0]['message']['text']
    except:
        return 'OK'

    prompt = f"""
あなたはメルカリ販売のプロです。
以下の商品情報から売れるタイトル・説明文・価格を作ってください。

商品情報:
{user_message}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = response['choices'][0]['message']['content']

    print(reply)

    return 'OK'

if __name__ == "__main__":
    app.run()
