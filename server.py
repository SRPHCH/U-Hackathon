"""Antistant local server.

Serves the website and keeps the API keys on the server side:
  - Put your keys in keys.env (copy keys.example.env). That file is never sent to the browser and is git-ignored.
  - The browser talks only to /api/... on this server; the server adds the key and forwards to Gemini / ElevenLabs.

Run:  python server.py        then open  http://127.0.0.1:8765/
Python 3.9+ standard library only.
"""
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE = os.path.join(ROOT, "keys.env")


def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path, encoding="utf8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    # real environment variables win over the file
    for k in list(env) + ["GEMINI_API_KEY", "ELEVENLABS_API_KEY", "ACCESS_PASSWORD", "HOST", "PORT", "GEMINI_MODEL_LITE", "GEMINI_MODEL_THINK",
                          "ELEVENLABS_MODEL", "ELEVENLABS_VOICE_ID", "DAILY_CALL_LIMIT"]:
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


CFG = load_env(KEYS_FILE)
GEMINI_KEY = CFG.get("GEMINI_API_KEY", "")
ELEVEN_KEY = CFG.get("ELEVENLABS_API_KEY", "")
ACCESS_PASSWORD = CFG.get("ACCESS_PASSWORD", "")
# on a host like Railway the platform sets PORT and the server must listen on all interfaces
HOST = CFG.get("HOST") or ("0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
PORT = int(CFG.get("PORT", "8765"))
DAILY_LIMIT = int(CFG.get("DAILY_CALL_LIMIT", "3000"))   # hard cap on proxied API calls per day for the whole site (protects the keys)
MODEL_LITE = CFG.get("GEMINI_MODEL_LITE", "gemini-3.5-flash-lite")
MODEL_THINK = CFG.get("GEMINI_MODEL_THINK", "gemini-3.8-flash")
ELEVEN_MODEL = CFG.get("ELEVENLABS_MODEL", "eleven_v3")
ELEVEN_VOICE = CFG.get("ELEVENLABS_VOICE_ID", "")

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
ELEVEN_BASE = "https://api.elevenlabs.io/v1"
MODEL_RE = re.compile(r"^gemini-[A-Za-z0-9.\-]{1,60}$")
VOICE_RE = re.compile(r"^[A-Za-z0-9]{8,40}$")
MAX_BODY = 200_000            # bytes per API request
RATE_LIMIT = (120, 600)       # at most 120 API calls per client per 10 minutes

_hits = defaultdict(deque)
_lock = threading.Lock()
_day = {"d": "", "n": 0}


def day_ok():
    today = time.strftime("%Y-%m-%d")
    with _lock:
        if _day["d"] != today:
            _day["d"], _day["n"] = today, 0
        if _day["n"] >= DAILY_LIMIT:
            return False
        _day["n"] += 1
        return True


def rate_ok(ip):
    now = time.time()
    with _lock:
        q = _hits[ip]
        while q and now - q[0] > RATE_LIMIT[1]:
            q.popleft()
        if len(q) >= RATE_LIMIT[0]:
            return False
        q.append(now)
        return True


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        # never log query strings or bodies (nothing secret is in them, but keep logs short)
        sys.stderr.write("%s %s\n" % (self.command, self.path.split("?")[0]))

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    # ---------- static files: never serve secrets or the git folder ----------
    def _blocked_path(self):
        p = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        parts = [x for x in p.split("/") if x]
        if any(x.startswith(".") for x in parts):
            return True
        name = parts[-1].lower() if parts else ""
        return name.endswith(".env") or name in ("server.py",)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.api("GET")
        if self.path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/solora-landing.html")
            self.end_headers()
            return
        if self._blocked_path():
            return self.send_error(404)
        return super().do_GET()

    def do_HEAD(self):
        if self.path.startswith("/api/") or self._blocked_path():
            return self.send_error(404)
        return super().do_HEAD()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self.api("POST")
        return self.send_error(405)

    # ---------- API proxy ----------
    def reply_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def guard(self):
        """Lock: only this site's own pages may use the proxy, optionally behind a password."""
        if self.headers.get("X-Antistant") != "1":
            return self.reply_json(403, {"error": {"message": "forbidden"}}) or False
        origin = self.headers.get("Origin")
        host = self.headers.get("Host", "")
        if origin and urllib.parse.urlsplit(origin).netloc != host:
            return self.reply_json(403, {"error": {"message": "forbidden origin"}}) or False
        if ACCESS_PASSWORD and self.headers.get("X-Antistant-Pass", "") != ACCESS_PASSWORD:
            return self.reply_json(401, {"error": {"message": "password required"}}) or False
        fwd = (self.headers.get("X-Forwarded-For") or "").split(",")[0].strip()   # real client IP behind a proxy such as Railway
        if not rate_ok(fwd or self.client_address[0]):
            return self.reply_json(429, {"error": {"message": "too many requests, try again later"}}) or False
        if not day_ok():
            return self.reply_json(429, {"error": {"message": "daily limit reached, try again tomorrow"}}) or False
        return True

    def read_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            raise ValueError("request too large")
        return self.rfile.read(n) if n else b""

    def forward(self, url, method="GET", body=None, headers=None, raw=False):
        req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data, code, ctype = r.read(), r.status, r.headers.get("Content-Type", "application/json")
        except urllib.error.HTTPError as e:
            data, code, ctype = e.read(), e.code, e.headers.get("Content-Type", "application/json")
        except Exception as e:  # network problems
            return self.reply_json(502, {"error": {"message": "upstream error: %s" % e.__class__.__name__}})
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def api(self, method):
        path = urllib.parse.urlsplit(self.path).path
        if path == "/api/status" and method == "GET":
            # tells the page what is available, never the keys themselves
            return self.reply_json(200, {"gemini": bool(GEMINI_KEY), "eleven": bool(ELEVEN_KEY), "locked": bool(ACCESS_PASSWORD),
                                         "models": {"lite": MODEL_LITE, "think": MODEL_THINK}, "eleven_model": ELEVEN_MODEL, "eleven_voice": ELEVEN_VOICE})
        if not self.guard():
            return
        try:
            body = self.read_body() if method == "POST" else None
        except ValueError as e:
            return self.reply_json(413, {"error": {"message": str(e)}})

        m = re.match(r"^/api/gemini/models/([^/:]+):generateContent$", path)
        if m and method == "POST":
            if not GEMINI_KEY:
                return self.reply_json(503, {"error": {"message": "Gemini key is not set on the server (keys.env)"}})
            model = m.group(1)
            if not MODEL_RE.match(model):
                return self.reply_json(400, {"error": {"message": "invalid model"}})
            return self.forward("%s/models/%s:generateContent" % (GEMINI_BASE, model), "POST", body,
                                {"Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY})
        if path == "/api/gemini/models" and method == "GET":
            if not GEMINI_KEY:
                return self.reply_json(503, {"error": {"message": "Gemini key is not set on the server (keys.env)"}})
            return self.forward(GEMINI_BASE + "/models?pageSize=200", headers={"x-goog-api-key": GEMINI_KEY})

        m = re.match(r"^/api/eleven/tts/([^/]+)$", path)
        if m and method == "POST":
            if not ELEVEN_KEY:
                return self.reply_json(503, {"error": {"message": "ElevenLabs key is not set on the server (keys.env)"}})
            voice = m.group(1)
            if not VOICE_RE.match(voice):
                return self.reply_json(400, {"error": {"message": "invalid voice"}})
            return self.forward("%s/text-to-speech/%s?output_format=mp3_44100_128" % (ELEVEN_BASE, voice), "POST", body,
                                {"Content-Type": "application/json", "Accept": "audio/mpeg", "xi-api-key": ELEVEN_KEY})
        if path in ("/api/eleven/voices", "/api/eleven/models") and method == "GET":
            if not ELEVEN_KEY:
                return self.reply_json(503, {"error": {"message": "ElevenLabs key is not set on the server (keys.env)"}})
            return self.forward(ELEVEN_BASE + path[len("/api/eleven"):], headers={"xi-api-key": ELEVEN_KEY})

        return self.reply_json(404, {"error": {"message": "not found"}})


def main():
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print("Antistant running at http://%s:%d/" % ("127.0.0.1" if HOST in ("0.0.0.0", "") else HOST, PORT))
    print("  Gemini key: %s   ElevenLabs key: %s   Password lock: %s" % (
        "set" if GEMINI_KEY else "MISSING", "set" if ELEVEN_KEY else "MISSING", "on" if ACCESS_PASSWORD else "off"))
    if not os.path.exists(KEYS_FILE):
        print("  keys.env not found - copy keys.example.env to keys.env and fill in your keys")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
