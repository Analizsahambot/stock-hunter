from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Stock Hunter</h1>
    <p>تست اتصال به TSETMC</p>
    <a href="/test-tsetmc">تست TSETMC</a>
    """

@app.route("/test-tsetmc")
def test_tsetmc():

    url = "https://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch"

    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            },
            timeout=10
        )

        return jsonify({
            "status": "OK",
            "http_status": r.status_code,
            "content_length": len(r.content),
            "message": "Render توانست به TSETMC وصل شود"
        })

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "error_type": type(e).__name__,
            "error": str(e),
            "message": "Render نتوانست به TSETMC وصل شود"
        }), 500


@app.route("/health")
def health():
    return jsonify({"status": "OK"})


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
