from flask import Flask, request, jsonify
import requests
import json
import re

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
    "Referer": "https://trends.google.com/",
}

def clean_json(text):
    text = re.sub(r"^[^{\[]+", "", text)
    text = text.strip()
    return text

def fetch_google(url):
    r = requests.get(url, headers=HEADERS)
    if "<html" in r.text.lower():
        return {"error": "Google blocked the request (HTML returned)", "html": r.text[:500]}
    cleaned = clean_json(r.text)
    try:
        return json.loads(cleaned)
    except:
        return {"raw": cleaned}

#######################################################
# 1) TRENDS (GENEL TRENDLER)
#######################################################
@app.route("/trends")
def trends():
    geo = request.args.get("geo", "US")
    url = f"https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-180&geo={geo}"
    return jsonify(fetch_google(url))

#######################################################
# 2) SEARCH (BİR KELİMENİN POPÜLERLİĞİ)
#######################################################
@app.route("/search")
def search():
    q = request.args.get("q")
    geo = request.args.get("geo", "US")
    if not q:
        return jsonify({"error": "Missing q parameter"})
    url = f"https://trends.google.com/trends/api/relatedsearches?hl=en-US&tz=-180&geo={geo}&q={q}"
    return jsonify(fetch_google(url))

#######################################################
# 3) DAILY TRENDS — GERÇEK
#######################################################
@app.route("/daily")
def daily():
    geo = request.args.get("geo", "US")
    url = f"https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-180&geo={geo}"
    return jsonify(fetch_google(url))

#######################################################
# 4) REALTIME TRENDS
#######################################################
@app.route("/realtime")
def realtime():
    geo = request.args.get("geo", "US")
    cat = request.args.get("cat", "all")
    url = f"https://trends.google.com/trends/api/realtimetrends?hl=en-US&tz=-180&cat={cat}&geo={geo}"
    return jsonify(fetch_google(url))

#######################################################
# 5) EXPLORE — Interest Over Time
#######################################################
@app.route("/explore")
def explore():
    kw = request.args.get("keyword")
    geo = request.args.get("geo", "US")
    if not kw:
        return jsonify({"error": "Missing keyword"})
    url = (
        "https://trends.google.com/trends/api/explore?"
        f"hl=en-US&tz=-180&req=%7B%22comparisonItem%22:%5B%7B%22keyword%22:%22{kw}%22,%22geo%22:%22{geo}%22,%22time%22:%22today+12-m%22%7D%5D,%22category%22:0,%22property%22:%22%22%7D"
    )
    return jsonify(fetch_google(url))

#######################################################
# 6) RELATED QUERIES / TOPICS
#######################################################
@app.route("/related")
def related():
    kw = request.args.get("keyword")
    geo = request.args.get("geo", "US")
    if not kw:
        return jsonify({"error": "Missing keyword"})
    url = (
        "https://trends.google.com/trends/api/relatedSearches?"
        f"hl=en-US&tz=-180&req=%7B%22restriction%22:%7B%22geo%22:%7B%22country%22:%22{geo}%22%7D,%22keyword%22:%22{kw}%22,%22time%22:%22today+12-m%22%7D%7D"
    )
    return jsonify(fetch_google(url))

#######################################################
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Google Trends Full API aktif",
        "endpoints": [
            "/trends?geo=US",
            "/search?q=bitcoin&geo=US",
            "/daily?geo=US",
            "/realtime?geo=US&cat=all",
            "/explore?keyword=bitcoin&geo=US",
            "/related?keyword=bitcoin&geo=US"
        ]
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

