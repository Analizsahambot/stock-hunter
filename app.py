from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

BASE_URL = "https://cdn.tsetmc.com/api"

SYMBOLS = ["وبملت", "فملی", "شستا", "خودرو", "دتول"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Android 10; Mobile) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json",
}


def api_get(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )
    response.raise_for_status()
    return response.json()


def find_symbol(symbol):
    url = f"{BASE_URL}/Instrument/GetInstrumentSearch/{symbol}"
    data = api_get(url)

    results = data.get("instrumentSearch", [])

    if not results:
        return None

    # پیدا کردن دقیق‌ترین تطابق
    for item in results:
        if item.get("lVal18AFC") == symbol:
            return item

    return results[0]


def get_symbol_data(symbol):

    instrument = find_symbol(symbol)

    if not instrument:
        return {
            "symbol": symbol,
            "error": "نماد پیدا نشد"
        }

    ins_code = instrument.get("insCode")

    price_data = api_get(
        f"{BASE_URL}/ClosingPrice/GetClosingPriceInfo/{ins_code}"
    )

    order_data = api_get(
        f"{BASE_URL}/BestLimits/{ins_code}"
    )

    price = price_data.get("closingPriceInfo", {})
    orders = order_data.get("bestLimits", [])

    buy = []
    sell = []

    for row in orders:

        buy.append({
            "price": row.get("pMeDem", 0),
            "volume": row.get("qTitMeDem", 0),
            "orders": row.get("zOrdMeDem", 0)
        })

        sell.append({
            "price": row.get("pMeOf", 0),
            "volume": row.get("qTitMeOf", 0),
            "orders": row.get("zOrdMeOf", 0)
        })

    # سطح اول سفارشات
    buy_volume = buy[0]["volume"] if buy else 0
    sell_volume = sell[0]["volume"] if sell else 0

    # قدرت صف
    total_queue = buy_volume + sell_volume

    if total_queue > 0:
        queue_ratio = buy_volume / total_queue
    else:
        queue_ratio = 0.5

    # امتیاز اولیه
    score = int(queue_ratio * 100)

    return {
        "symbol": symbol,
        "ins_code": ins_code,

        "price": {
            "last": price.get("pDrCotVal"),
            "close": price.get("pClosing"),
            "yesterday": price.get("priceYesterday"),
            "low": price.get("priceMin"),
            "high": price.get("priceMax"),
            "volume": price.get("qTotTran5J"),
            "trades": price.get("zTotTran")
        },

        "orderbook": {
            "buy": buy[:5],
            "sell": sell[:5]
        },

        "queue": {
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "score": score
        }
    }


@app.route("/")
def home():

    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">

    <head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <title>Stock Hunter</title>

    <style>

    body {
        font-family: Tahoma;
        background: #f5f5f5;
        padding: 20px;
    }

    .card {
        background: white;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 8px #ddd;
    }

    button {
        padding: 12px 25px;
        border: none;
        border-radius: 10px;
        background: #111;
        color: white;
        font-size: 16px;
    }

    </style>

    </head>

    <body>

    <div class="card">

    <h1>🔎 Stock Hunter</h1>

    <p>
    شکارچی صف و قدرت سفارشات TSETMC
    </p>

    <button onclick="scan()">
    🔄 اسکن بازار
    </button>

    </div>

    <div id="result"></div>

    <script>

    async function scan() {

        document.getElementById("result").innerHTML =
        "<div class='card'>⏳ در حال دریافت اطلاعات TSETMC...</div>";

        const response =
        await fetch("/api/scan");

        const data =
        await response.json();

        let html = "";

        data.forEach(item => {

            if(item.error) {

                html += `
                <div class="card">
                ❌ ${item.symbol}
                <br>
                ${item.error}
                </div>
                `;

                return;
            }

            const p = item.price;
            const q = item.queue;

            html += `

            <div class="card">

            <h2>${item.symbol}</h2>

            <p>
            💰 آخرین قیمت:
            ${p.last ?? "-"}
            </p>

            <p>
            📊 حجم معاملات:
            ${p.volume ?? "-"}
            </p>

            <hr>

            <p>
            🟢 صف خرید:
            ${q.buy_volume.toLocaleString()}
            </p>

            <p>
            🔴 صف فروش:
            ${q.sell_volume.toLocaleString()}
            </p>

            <p>
            🎯 امتیاز:
            <strong>${q.score}/100</strong>
            </p>

            </div>

            `;

        });

        document.getElementById("result").innerHTML = html;
    }

    </script>

    </body>

    </html>
    """


@app.route("/api/scan")
def scan():

    results = []

    for symbol in SYMBOLS:

        try:

            results.append(
                get_symbol_data(symbol)
            )

            # جلوگیری از فشار روی TSETMC
            time.sleep(0.7)

        except Exception as e:

            results.append({
                "symbol": symbol,
                "error": str(e)
            })

    return jsonify(results)


@app.route("/health")
def health():

    return jsonify({
        "status": "OK"
    })


if __name__ == "__main__":

    import os

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
