#!/usr/bin/env python3
"""Same-origin local preview: independent /aibox/ files plus an isolated main-site dev server."""
import argparse
import http.server
import pathlib
import urllib.request
import urllib.error
from urllib.parse import urlsplit
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=8768)
parser.add_argument('--main', default='http://127.0.0.1:5178')
args = parser.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw): super().__init__(*a, directory=str(root), **kw)
    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ['/aibox', '/aibox/en', '/aibox/init']:
            self.send_response(308); self.send_header('Location', self.path.replace(path,path+'/')); self.end_headers(); return
        if path.startswith('/aibox/'):
            self.path = self.path[len('/aibox'):]
            return super().do_GET()
        self.proxy()
    def do_POST(self): self.proxy()
    def proxy(self):
        body = self.rfile.read(int(self.headers.get('Content-Length','0'))) if self.command=='POST' else None
        headers = {k:v for k,v in self.headers.items() if k.lower() not in ['connection','host','accept-encoding']}
        req = urllib.request.Request(args.main+self.path, data=body, headers=headers, method=self.command)
        try: response=urllib.request.urlopen(req, timeout=60)
        except urllib.error.HTTPError as error: response=error
        except urllib.error.URLError:
            self.send_error(502); return
        with response:
            self.send_response(response.status)
            for k,v in response.headers.items():
                if k.lower() not in ['connection','transfer-encoding','content-length','content-encoding']: self.send_header(k,v)
            data=response.read(); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
http.server.ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
