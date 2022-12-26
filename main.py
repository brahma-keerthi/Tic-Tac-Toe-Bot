#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        webbrowser.open_new_tab(f"http://127.0.0.1:{PORT}")
        httpd.serve_forever()
