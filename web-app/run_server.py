#!/usr/bin/env python3
"""
Simple HTTP server for web app
"""
import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

# ⭐ FIX: Force UTF-8 output
sys.stdout.reconfigure(encoding="utf-8", errors="ignore")

PORT = 8080
WEB_DIR = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Custom log format
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
            print(f"✅ Server started on port {PORT}")
            print("Press Ctrl+C to stop\n")
            
            # Open browser automatically
            webbrowser.open(f'http://localhost:{PORT}')
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 98:  # Port already in use
            print(f"❌ Port {PORT} is already in use!")
            print("Try:")
            print("  1. Kill the process using port 8080")
            print("  2. Use a different port")
            print("  3. Restart the server")
        else:
            print(f"❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()