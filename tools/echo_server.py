#!/usr/bin/env python3
"""
Simple HTTP echo server for debugging Trustify DA clients.
Listens on port 8082 and logs all incoming requests to stdout.
"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime


class EchoHandler(BaseHTTPRequestHandler):
    """HTTP handler that logs all requests and returns a valid response"""

    def log_request_details(self):
        """Log complete request details to stdout"""
        timestamp = datetime.now().isoformat()

        # Read body if present
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''

        # Print separator
        print("\n" + "="*80)
        print(f"REQUEST at {timestamp}")
        print("="*80)

        # Print request line
        print(f"{self.command} {self.path} {self.request_version}")

        # Print headers
        print("\nHeaders:")
        for header, value in self.headers.items():
            print(f"  {header}: {value}")

        # Print body
        if body:
            print("\nBody:")
            try:
                # Try to pretty-print JSON
                body_json = json.loads(body.decode('utf-8'))
                print(json.dumps(body_json, indent=2))
            except:
                # Fall back to raw output
                print(body.decode('utf-8', errors='replace'))

        print("="*80)
        sys.stdout.flush()

        return body

    def send_json_response(self, data, status=200):
        """Send a JSON response"""
        response = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)

    def do_GET(self):
        """Handle GET requests"""
        self.log_request_details()
        self.send_json_response({"status": "ok", "method": "GET", "path": self.path})

    def do_POST(self):
        """Handle POST requests"""
        body = self.log_request_details()

        # Return a minimal valid response that looks like a Trustify DA response
        response = {
            "providers": {
                "tpa1": {
                    "sources": {
                        "osv-github": {
                            "dependencies": []
                        }
                    }
                }
            },
            "scanned": {
                "direct": 0,
                "total": 0,
                "transitive": 0
            }
        }

        self.send_json_response(response)

    def do_PUT(self):
        """Handle PUT requests"""
        self.log_request_details()
        self.send_json_response({"status": "ok", "method": "PUT", "path": self.path})

    def do_DELETE(self):
        """Handle DELETE requests"""
        self.log_request_details()
        self.send_json_response({"status": "ok", "method": "DELETE", "path": self.path})

    def log_message(self, format, *args):
        """Override to suppress default logging"""
        pass


def main():
    host = '0.0.0.0'
    port = 8082

    server = HTTPServer((host, port), EchoHandler)

    print(f"Echo server listening on http://{host}:{port}")
    print("All requests will be logged to stdout")
    print("Press Ctrl+C to stop")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()


if __name__ == '__main__':
    main()
