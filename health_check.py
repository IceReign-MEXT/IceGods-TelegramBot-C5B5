import http.server
import socketserver
import threading
import os

def run_server():
    PORT = int(os.getenv("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    # Allow address reuse to prevent "Port already in use" errors on restart
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"📡 Health Check LIVE on Port {PORT}")
        httpd.serve_forever()

def start_ping_listener():
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
