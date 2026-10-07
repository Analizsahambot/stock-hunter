from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Stock Hunter</title>
    </head>
    <body style="font-family:Tahoma;text-align:center;padding:40px">
        <h1>🔎 Stock Hunter</h1>
        <h2>نسخه V1</h2>
        <p>سیستم شکار صف TSETMC در حال راه‌اندازی است.</p>
        <p>وبملت | فملی | شستا | خودرو | دتول</p>
        <p>✅ Server is running</p>
    </body>
    </html>
    """

@app.route("/health")
def health():
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
