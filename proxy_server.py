#!/usr/bin/env python3
"""
Tenable GraphQL CORS proxy — local Python server (standard library only)
------------------------------------------------------------------------
Run:
    python3 proxy_server.py            # default port 8787
    python3 proxy_server.py 9000       # custom port

Then put  http://localhost:8787/  in the report's "Proxy URL" field and open
the report over http (e.g. `python3 -m http.server 8000`) or from file://.

The browser sends  Authorization: Bearer <token>  to this server; it forwards
that header to Tenable and adds the CORS headers the browser requires.
Nothing is stored or logged beyond a short request line.

No pip install required — uses only the Python standard library (3.7+).
"""

import sys
import json
import ssl
import http.client
from http.server import HTTPServer, BaseHTTPRequestHandler

TARGET_HOST = "app.tenable.com"
TARGET_PATH = "/api/graph"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
ALLOW_ORIGIN = "*"          # restrict to your page origin in production
SSL_CTX = ssl.create_default_context()


class ProxyHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # suppress default access-log noise

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", ALLOW_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Max-Age", "86400")

    def _reply(self, status, data, ct="application/json"):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        # Friendly response so opening the URL in a browser confirms it's up.
        self._reply(200, b"Tenable GraphQL proxy is running. Send POST requests here.",
                    "text/plain")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""

        token = self.headers.get("Authorization", "")
        preview = (token[:16] + "…") if len(token) > 16 else (token or "(missing!)")
        print(f"  → POST https://{TARGET_HOST}{TARGET_PATH}   auth: {preview}")

        fwd = {
            "Content-Type": "application/json",
            "Authorization": token,
            "Host": TARGET_HOST,
        }

        try:
            conn = http.client.HTTPSConnection(TARGET_HOST, 443, context=SSL_CTX)
            conn.request("POST", TARGET_PATH, body=body, headers=fwd)
            resp = conn.getresponse()
            data = resp.read()
            conn.close()
        except Exception as e:
            print(f"    ERROR: {e}")
            self._reply(502, json.dumps({"errors": [{"message": "Proxy error: " + str(e)}]}).encode())
            return

        print(f"    ← {resp.status} {resp.reason} ({len(data)} bytes)")
        ct = resp.getheader("Content-Type", "application/json")
        self._reply(resp.status, data, ct)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), ProxyHandler)
    print("\n  Tenable GraphQL CORS proxy")
    print(f"  Listening : http://localhost:{PORT}/")
    print(f"  Forwarding: https://{TARGET_HOST}{TARGET_PATH}")
    print(f"\n  Paste  http://localhost:{PORT}/  into the report's Proxy URL field.")
    print("  Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
