from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Google Trends Proxy is running. Use /daily?geo=US or /search?q=bitcoin&geo=US"
    })

@app.route("/daily")
def daily():
    geo = request.args.get("geo", "US")
    url = f"https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-480&geo={geo}"

    r = requests.get(url, headers=HEADERS)
    text = r.text.replace(")]}',", "").strip()

    return app.response_class(
        response=text,
        status=200,
        mimetype='application/json'
    )

@app.route("/search")
def search():
    q = request.args.get("q")
    geo = request.args.get("geo", "US")
    
    if not q:
        return jsonify({"error": "Missing parameter: q"})

    url = (
        f"https://trends.google.com/trends/api/explore?"
        f"hl=en-US&tz=-480&req=%7B%22comparisonItem%22:%5B%7B%22keyword%22:%22{q}%22,"
        f"%22geo%22:%22{geo}%22,%22time%22:%22today%2012-m%22%7D%5D,%22category%22:0,"
        f"%22property%22:%22%22%7D"
    )

    r = requests.get(url, headers=HEADERS)
    text = r.text.replace(")]}',", "").strip()

    return app.response_class(
        response=text,
        status=200,
        mimetype='application/json'
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
