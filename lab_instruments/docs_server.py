"""Serve the bundled Python API docs as a static site and open in browser.

Usage:
    scpi-docs           # serve Python API docs (default)
    scpi-docs python    # same as above
    scpi-docs repl      # serve REPL command reference
"""

import http.server
import pathlib
import sys
import threading
import webbrowser


def main():
    variant = sys.argv[1].lower() if len(sys.argv) > 1 else "python"
    if variant in ("-h", "--help"):
        print(__doc__.strip())
        return

    lab_pkg = pathlib.Path(__file__).resolve().parent

    if variant == "repl":
        site_dir = lab_pkg / "site"
        label = "REPL command"
    else:
        site_dir = lab_pkg / "site-library"
        label = "Python API"

    index = site_dir / "index.html"
    if not index.exists():
        print(f"No built {label} docs found at {site_dir}")
        print("Run: pip install mkdocs-material && mkdocs build -f mkdocs-library.yml")
        sys.exit(1)

    _site = str(site_dir)

    class _QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=_site, **kw)

        def log_message(self, fmt, *a):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), _QuietHandler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()

    url = f"http://127.0.0.1:{port}/index.html"
    print(f"{label} docs: {url}")
    print("Press Ctrl+C to stop.")
    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.shutdown()
