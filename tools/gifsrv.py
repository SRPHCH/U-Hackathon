import http.server, os, base64, json
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")
class H(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); d = json.loads(self.rfile.read(n))
        data = d["url"].split(",", 1)[1]
        open(os.path.join(OUT, "f%02d.png" % d["i"]), "wb").write(base64.b64decode(data))
        self.send_response(200); self._cors(); self.end_headers(); self.wfile.write(b"ok")
    def log_message(self, *a): pass
http.server.HTTPServer(("127.0.0.1", 8766), H).serve_forever()
