#!/usr/bin/env python3
"""
Tenable FinOps Report — all-in-one launcher (Python standard library only)
--------------------------------------------------------------------------
Serves the HTML report AND proxies its GraphQL calls to Tenable from the same
origin, then opens your browser straight to the report. One command, no CORS,
no separate static server, no Proxy URL to paste.

Run:
    python3 proxy_server.py             # serves on http://localhost:8787 and opens the report
    python3 proxy_server.py 9000        # custom port
    python3 proxy_server.py --no-browser  # don't auto-open the browser

What happens:
  • GET  /                      -> the report (aws-finops-waste-report.html)
  • GET  /<file>                -> static files from this folder
  • POST /api/graph             -> forwarded to https://app.tenable.com/api/graph
                                   with your Authorization: Bearer header

Because the page and the proxy share an origin, the browser makes no
cross-origin request — so there is nothing for CORS to block. Just enter your
Tenable bearer token in the report and click Connect.

No pip install required (Python 3.7+).
"""

import os
import sys
import json
import ssl
import threading
import webbrowser
import http.client
from http.server import HTTPServer, BaseHTTPRequestHandler

TARGET_HOST = "app.tenable.com"
TARGET_PATH = "/api/graph"
PROXY_PATH = "/api/graph"            # local path the report POSTs to
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_FILE = "aws-finops-waste-report.html"
ALLOW_ORIGIN = "*"
SSL_CTX = ssl.create_default_context()

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
}


def pick_report():
    """Return the report filename, falling back to the first .html in the folder."""
    if os.path.isfile(os.path.join(BASE_DIR, REPORT_FILE)):
        return REPORT_FILE
    for f in sorted(os.listdir(BASE_DIR)):
        if f.lower().endswith(".html"):
            return f
    return REPORT_FILE


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # quiet default access log

    # ---- helpers ----
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", ALLOW_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send(self, status, body, ctype="text/plain; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _safe_path(self, url_path):
        """Resolve a URL path to a file inside BASE_DIR, or None if invalid."""
        rel = url_path.split("?", 1)[0].lstrip("/")
        if rel in ("", "/"):
            rel = pick_report()
        target = os.path.normpath(os.path.join(BASE_DIR, rel))
        if not target.startswith(BASE_DIR + os.sep) and target != BASE_DIR:
            return None
        return target if os.path.isfile(target) else None

    # ---- routes ----
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path.rstrip("/") == PROXY_PATH:
            self._send(405, "Use POST for the GraphQL endpoint.")
            return
        target = self._safe_path(self.path)
        if not target:
            self._send(404, "Not found.")
            return
        ext = os.path.splitext(target)[1].lower()
        ctype = CONTENT_TYPES.get(ext, "application/octet-stream")
        with open(target, "rb") as fh:
            self._send(200, fh.read(), ctype)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path.rstrip("/") != PROXY_PATH:
            self._send(404, "Not found.")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        token = self.headers.get("Authorization", "")
        preview = (token[:16] + "…") if len(token) > 16 else (token or "(missing!)")
        print(f"  → POST https://{TARGET_HOST}{TARGET_PATH}   auth: {preview}")

        fwd = {"Content-Type": "application/json", "Authorization": token, "Host": TARGET_HOST}
        try:
            conn = http.client.HTTPSConnection(TARGET_HOST, 443, context=SSL_CTX)
            conn.request("POST", TARGET_PATH, body=body, headers=fwd)
            resp = conn.getresponse()
            data = resp.read()
            conn.close()
        except Exception as e:
            print(f"    ERROR: {e}")
            self._send(502, json.dumps({"errors": [{"message": "Proxy error: " + str(e)}]}),
                       "application/json")
            return

        print(f"    ← {resp.status} {resp.reason} ({len(data)} bytes)")
        ctype = resp.getheader("Content-Type", "application/json")
        self._send(resp.status, data, ctype)


def main():
    args = [a for a in sys.argv[1:]]
    open_browser = "--no-browser" not in args
    args = [a for a in args if a != "--no-browser"]
    port = int(args[0]) if args and args[0].isdigit() else 8787

    report = pick_report()
    url = f"http://localhost:{port}/?proxy={PROXY_PATH}"

    server = HTTPServer(("127.0.0.1", port), Handler)
    print("\n  Tenable FinOps Report — all-in-one launcher")
    print(f"  Report : {url}")
    print(f"  Proxy  : POST http://localhost:{port}{PROXY_PATH}  ->  https://{TARGET_HOST}{TARGET_PATH}")
    print(f"  Serving: {os.path.join(BASE_DIR, report)}")
    print("\n  Enter your Tenable bearer token in the report and click Connect.")
    print("  Ctrl+C to stop.\n")

    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")


if __name__ == "__main__":
    main()
