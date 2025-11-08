from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

def crawl_site(base_url, limit=100, exclude=[]):
    domain = urlparse(base_url).netloc
    visited = set()

    def crawl(url):
        if url in visited or len(visited) >= limit:
            return
        if any(ex in url for ex in exclude):
            return

        visited.add(url)
        try:
            print(f"Crawling: {url}")
            response = requests.get(url, timeout=10)
            if "text/html" not in response.headers.get("Content-Type", ""):
                return

            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])
                if urlparse(full_url).netloc == domain:
                    crawl(full_url)
        except Exception as e:
            print(f"Error crawling {url}: {e}")

    crawl(base_url)
    return sorted(visited)

@app.route("/generate_sitemap", methods=["GET"])
def generate_sitemap():
    site = request.args.get("url")
    limit = int(request.args.get("limit", 50))
    exclude = request.args.getlist("exclude")

    if not site:
        return jsonify({"error": "Missing ?url parameter"}), 400

    urls = crawl_site(site, limit, exclude)
    return jsonify({
        "site": site,
        "total": len(urls),
        "limit": limit,
        "urls": urls
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)