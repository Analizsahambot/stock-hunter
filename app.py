from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html lang="fa" dir="rtl">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <body style="font-family:Tahoma;text-align:center;padding:40px">
        <h1>🔎 Stock Hunter</h1>
        <h2>نسخه V1</h2>
        <p>سیستم شکار صف TSETMC در حال راه‌اندازی است.</p>
        <p>وبملت | فملی | شستا | خودرو | دتول</p>
    </body>
    </html>
    """

@app.route("/health")
def health():
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
