from flask import redirect, jsonify, Flask, render_template, request
import requests
from threading import Thread
from time import sleep

app = Flask(__name__)

URLS = {}

def ping():
    while True:
        for url in URLS:
            try:
                response = requests.get(URLS[url]["url"], timeout=5)
                if response.status_code == 200:
                    URLS[url]["status"] = "online"
                else:
                    URLS[url]["status"] = "offline"
                
                URLS[url]["status-code"] = response.status_code

            except requests.exceptions.RequestException as e:
                print(f"Error checking {url}: {e}")
                URLS[url]["status"] = "offline"
                URLS[url]["status-code"] = "server offline"
                continue
        sleep(100)

Thread(target=ping, daemon=True).start()

def check_url(url):
    print(f"Checking URL: {url}")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            URLS[url]["status"] = "online"
        else:
            URLS[url]["status"] = "offline"
        
        URLS[url]["status-code"] = response.status_code

    except requests.exceptions.RequestException as e:
        print(f"Error checking {url}: {e}")
        URLS[url]["status"] = "offline"
        URLS[url]["status-code"] = "server offline"

@app.route("/")
def home():
    print(f"Current URLs: {URLS}")
    return render_template("index.html", URLS=URLS)

@app.route("/add", methods=["POST"])
def add_url():
    url = request.form.get("url")
    URLS[url] = {"url": url, "status": "checking", "status-code": "checking.."}
    Thread(target=check_url, args=(url,), daemon=True).start()
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete_url():
    data = request.get_json()
    url = data.get("url")
    print(f"Deleting URL: {url}")
    URLS.pop(url, None)
    print(f"Current URLs: {URLS}")
    return redirect("/")

@app.route("/update", methods=["GET"])
def update():
    return jsonify(URLS)

if __name__ == "__main__":
    app.run(debug=True)
