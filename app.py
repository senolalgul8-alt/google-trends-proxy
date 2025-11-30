from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return {"error": f"Google returned HTTP {r.status_code}", "html": r.text}
        return r.json()
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Google Trends Proxy aktif",
        "endpoints": {
            "daily": "/daily?geo=US",
            "realtime": "/realtime?geo=US&cat=all",
            "search": "/search?q=bitcoin&geo=US",
            "related": "/related?q=bitcoin&geo=US"
        }
    })


# DAILY TRENDS
@app.route("/daily")
def daily():
    geo = request.args.get("geo", "US")
    url = f"https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-180&geo={geo}"
    return jsonify(fetch(url))


# REALTIME TRENDS
@app.route("/realtime")
def realtime():
    geo = request.args.get("geo", "US")
    cat = request.args.get("cat", "all")
    url = f"https://trends.google.com/trends/api/realtimetrends?hl=en-US&tz=-180&cat={cat}&fi=0&geo={geo}&ri=300&rs=15"
    return jsonify(fetch(url))


# SEARCH KEYWORD TREND
@app.route("/search")
def search():
    q = request.args.get("q")
    geo = request.args.get("geo", "US")

    if not q:
        return jsonify({"error": "Missing keyword"})

    url = f"https://trends.google.com/trends/api/explore?hl=en-US&tz=-180&req=%7B%22comparisonItem%22%3A%5B%7B%22keyword%22%3A%22{q}%22%2C%22geo%22%3A%22{geo}%22%2C%22time%22%3A%22today%2012-m%22%7D%5D%2C%22category%22%3A0%7D"

    return jsonify(fetch(url))


# RELATED QUERIES
@app.route("/related")
def related():
    q = request.args.get("q")
    geo = request.args.get("geo", "US")

    if not q:
        return jsonify({"error": "Missing keyword"})

    url = f"https://trends.google.com/trends/api/relatedsearches?hl=en-US&tz=-180&geo={geo}&keyword={q}"

    return jsonify(fetch(url))


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
