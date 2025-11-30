from flask import Flask, request, jsonify
import requests
import json
import re
import random
import time

app = Flask(__name__)

# Çok güçlü User-Agent listesi (random seçiliyor)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
]

def make_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
        "Referer": "https://trends.google.com/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1",
        "Sec-Ch-Ua": '"Chromium";v="120", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
    }

def clean_html(text):
    """Google HTML dönerse temizler."""
    return re.sub('<.*?>', '', text)

def fetch(url):
    """Google bloklarsa tekrar deneyen güçlü istek sistemi."""
    for attempt in range(3):
        try:
            headers = make_headers()
            r = requests.get(url, headers=headers, timeout=10)

            # HTML → Google engeli
            if "<html" in r.text.lower() or r.status_code in [403, 429]:
                if attempt < 2:
                    time.sleep(1.5)
                    continue
                return {"error": "Google blocked the request", "html": clean_html(r.text)}

            # JSON parse
            cleaned = clean_html(r.text)
            return json.loads(cleaned)

        except Exception as e:
            if attempt == 2:
                return {"error": str(e)}
            time.sleep(1)

    return {"error": "Unknown"}

########################################
### ENDPOINTS
########################################

@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Google Trends Proxy v2 active",
        "endpoints": [
            "/trends?geo=US",
            "/search?q=bitcoin&geo=US",
            "/daily?geo=US",
            "/realtime?geo=US&cat=all",
            "/explore?keyword=bitcoin&geo=US",
            "/related?keyword=bitcoin&geo=US"
        ]
    })

@app.route("/trends")
def trends():
    geo = request.args.get("geo", "US")
    url = f"https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-180&geo={geo}"
    return jsonify(fetch(url))

@app.route("/daily")
def daily():
    geo = request.args.get("geo", "US")
    url = f"https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-180&geo={geo}"
    return jsonify(fetch(url))

@app.route("/search")
def search():
    q = request.args.get("q")
    geo = request.args.get("geo", "US")

    if not q:
        return jsonify({"error": "Missing q parameter"})

    url = (
        "https://trends.google.com/trends/api/widgetdata/multiline?"
        f"hl=en-US&tz=-180&req=%7B%22time%22%3A%22today+12-m%22%2C%22keyword%22%3A%5B%22{q}%22%5D%2C%22geo%22%3A%22{geo}%22%7D"
    )
    return jsonify(fetch(url))

@app.route("/explore")
def explore():
    keyword = request.args.get("keyword")
    geo = request.args.get("geo", "US")

    if not keyword:
        return jsonify({"error": "Missing keyword"})

    url = (
        "https://trends.google.com/trends/api/explore?hl=en-US&tz=-180&req="
        f"%7B%22comparisonItem%22%3A%5B%7B%22keyword%22%3A%22{keyword}%22%2C%22geo%22%3A%22{geo}%22%2C%22time%22%3A%22today+12-m%22%7D%5D%2C"
        "%22category%22%3A0%2C%22property%22%3A%22%22%7D"
    )
    return jsonify(fetch(url))

@app.route("/realtime")
def realtime():
    geo = request.args.get("geo", "US")
    cat = request.args.get("cat", "all")

    url = (
        f"https://trends.google.com/trends/api/realtimetrends?hl=en-US&tz=-180&cat={cat}&geo={geo}"
    )
    return jsonify(fetch(url))

@app.route("/related")
def related():
    keyword = request.args.get("keyword")
    geo = request.args.get("geo", "US")

    if not keyword:
        return jsonify({"error": "Missing keyword"})

    url = (
        "https://trends.google.com/trends/api/relatedSearches?"
        f"hl=en-US&tz=-180&geo={geo}&keyword={keyword}&time=today+12-m"
    )
    return jsonify(fetch(url))

########################################

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
