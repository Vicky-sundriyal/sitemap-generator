from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Sitemap Generator is running! Use /generate?url=https://example.com to crawl."

@app.route('/generate')
def generate_sitemap():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"error": "Please provide a ?url=https://example.com"}), 400

    visited = set()
    queue = deque([target_url])
    sitemap = []

    while queue and len(visited) < 100:  # crawl limit
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            sitemap.append(url)
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if target_url in full_url and full_url not in visited:
                    queue.append(full_url)
        except Exception:
            continue

    return jsonify({"total": len(sitemap), "urls": list(sitemap)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
