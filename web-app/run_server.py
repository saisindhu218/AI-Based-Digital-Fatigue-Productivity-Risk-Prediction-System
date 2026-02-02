#!/usr/bin/env python3
"""
HTTP server with CORS support
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import webbrowser
import threading
import time
import os

PORT = 8080

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def open_browser():
    """Open browser after delay"""
    time.sleep(2)
    webbrowser.open(f"http://localhost:{PORT}")

if __name__ == "__main__":
    print("=" * 60)
    print("   Digital Fatigue Prediction System - Web App")
    print("=" * 60)

    print(f"📁 Serving directory: {os.getcwd()}")

    # Open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
            print(f"\n🌐 Serving at http://localhost:{PORT}")
            print("   CORS headers enabled")
            print("\n🛑 Press Ctrl+C to stop")
            print("=" * 60)

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nError: {e}")