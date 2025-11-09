from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag
from collections import deque

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return "✅ Sitemap Generator is running! Use /generate?url=https://example.com to crawl."

def crawl_website(target_url, limit=100):
    visited = set()
    queue = deque([target_url])
    sitemap = []

    while queue and len(visited) < limit:
        url = queue.popleft()
        url, _ = urldefrag(url)  # Remove #fragments like #main
        if url in visited:
            continue
        visited.add(url)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            sitemap.append(url)
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                full_url, _ = urldefrag(full_url)  # Remove fragments
                if target_url in full_url and full_url not in visited:
                    queue.append(full_url)
        except Exception:
            continue
    return sitemap

@app.route('/generate')
def generate_json():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"error": "Please provide ?url=https://example.com"}), 400
    sitemap = crawl_website(target_url)
    return jsonify({"total": len(sitemap), "urls": sitemap})

@app.route('/generate-txt')
def generate_txt():
    target_url = request.args.get('url')
    if not target_url:
        return "Error: Please provide ?url=https://example.com", 400
    sitemap = crawl_website(target_url)
    output = "\n".join(sitemap)
    return Response(output, mimetype="text/plain")

@app.route('/generate-xml')
def generate_xml():
    target_url = request.args.get('url')
    if not target_url:
        return "Error: Please provide ?url=https://example.com", 400
    sitemap = crawl_website(target_url)
    xml_output = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_output += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in sitemap:
        xml_output += f"  <url><loc>{url}</loc></url>\n"
    xml_output += "</urlset>"
    return Response(xml_output, mimetype="application/xml")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
