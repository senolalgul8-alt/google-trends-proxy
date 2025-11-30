
from flask import Flask, request, Response, jsonify
import requests
import json

app = Flask(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


@app.route("/")
def index():
    return jsonify({
        "status": "ok",
        "message": "Google Trends proxy is running. Use /trends?geo=US or /trends?q=bitcoin&geo=US"
    })


@app.route("/trends")
def trends():
    geo = request.args.get("geo", "US")
    q = request.args.get("q")

    try:
        if q:
            # Keyword-based explore endpoint
            req_obj = {
                "comparisonItem": [{
                    "keyword": q,
                    "geo": geo,
                    "time": "now 7-d"
                }],
                "category": 0,
                "property": ""
            }

            params = {
                "hl": "en-US",
                "tz": "0",
                "req": json.dumps(req_obj, separators=(",", ":")),
                "property": ""
            }
            url = "https://trends.google.com/trends/api/explore"
        else:
            # Daily trending searches endpoint
            params = {
                "hl": "en-US",
                "tz": "0",
                "geo": geo
            }
            url = "https://trends.google.com/trends/api/dailytrends"

        g_res = requests.get(url, params=params, headers=HEADERS, timeout=15)
        text = g_res.text.lstrip(")]}',\n ")

        resp = Response(text, status=g_res.status_code, mimetype="application/json")
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    except Exception as e:
        err = {"error": str(e)}
        return jsonify(err), 500


if __name__ == "__main__":
    # For local testing; Render will use gunicorn
    app.run(host="0.0.0.0", port=8000)
