#!/usr/bin/env python3
"""
Simple HTTP server for web app (Fixed Version)
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

# Force UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8", errors="ignore")

PORT = 8080
WEB_DIR = Path(__file__).parent.resolve()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        """
        Fix routing:
        /  -> index.html
        """

        # ROOT ROUTE FIX
        if self.path in ("/", ""):
            self.path = "/index.html"

        # If file doesn't exist → try .html
        requested = WEB_DIR / self.path.strip("/")
        if not requested.exists():
            alt = WEB_DIR / (self.path.strip("/") + ".html")
            if alt.exists():
                self.path = "/" + alt.name

        return super().do_GET()

    def end_headers(self):
        """Allow frontend JS API calls"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[WEB] {self.address_string()} - {format % args}")


def main():
    os.chdir(WEB_DIR)

    print("=" * 60)
    print("Digital Fatigue Guard - Web Application Server")
    print("=" * 60)
    print(f"Serving from: {WEB_DIR}")
    print(f"Local URL: http://localhost:{PORT}")
    print("=" * 60)

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Server started on port {PORT}")
            print("Press Ctrl+C to stop\n")

            # Auto-open browser
            webbrowser.open(f"http://localhost:{PORT}")

            httpd.serve_forever()

    except OSError:
        print(f"\nPort {PORT} already in use.")
        print("Close other servers or change port number.")

    except KeyboardInterrupt:
        print("\nServer stopped")

    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()