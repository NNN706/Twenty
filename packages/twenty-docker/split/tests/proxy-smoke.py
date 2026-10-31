#!/usr/bin/env python3
"""Exercise the production Nginx template against a mock API on a Linux CI runner.

No application image is built locally: this uses the public Nginx base image.
This checks proxy behavior, not Twenty authentication or database migrations.
"""
import http.server
import json
import pathlib
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
received = []


class API(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        received.append((self.path, dict(self.headers)))
        data = json.dumps({'path': self.path}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Set-Cookie', 'session=smoke; HttpOnly; SameSite=Lax')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length', 0)))
        self.do_GET()

    def log_message(self, *args):
        pass


api = http.server.ThreadingHTTPServer(('0.0.0.0', 18080), API)
threading.Thread(target=api.serve_forever, daemon=True).start()
container = 'twenty-split-proxy-smoke'


def request(path, method='GET'):
    req = urllib.request.Request('http://127.0.0.1:8080' + path,
                                 headers={'Host': 'sales.example.net',
                                          'X-Forwarded-Proto': 'https'},
                                 method=method)
    return urllib.request.urlopen(req, timeout=5)


try:
    with tempfile.TemporaryDirectory() as directory:
        temp = pathlib.Path(directory)
        static = temp / 'static'
        static.mkdir()
        (static / 'index.html').write_text('<html>SPA smoke</html>')
        (static / 'env-config.js').write_text((ROOT / 'twenty-front/env-config.js').read_text())
        conf = (ROOT / 'twenty-front/default.conf.template').read_text()
        (temp / 'default.conf').write_text(conf)
        subprocess.run(['docker', 'run', '--detach', '--rm', '--name', container,
                        '--network', 'host',
                        '-e', 'BACKEND_UPSTREAM=http://127.0.0.1:18080',
                        '-e', 'NGINX_ENVSUBST_FILTER=^BACKEND_UPSTREAM$',
                        '-v', f'{temp}/default.conf:/etc/nginx/templates/default.conf.template:ro',
                        '-v', f'{static}:/usr/share/nginx/html:ro',
                        'nginx:stable-alpine'], check=True)
        for attempt in range(30):
            try:
                assert request('/frontend-healthz').read() == b'ok\n'
                break
            except (OSError, AssertionError):
                time.sleep(1)
        else:
            raise RuntimeError('Nginx did not become ready')
        response = request('/settings/profile')
        assert b'SPA smoke' in response.read()
        response = request('/env-config.js')
        assert 'no-store' in response.headers['Cache-Control']
        assert b'window.location.origin' in response.read()
        assert 'no-store' in request('/index.html').headers['Cache-Control']
        paths = ['/graphql', '/metadata', '/rest/companies?a=1', '/auth/google',
                 '/client-config', '/file/x/id', '/public-assets/w/a/icon.svg',
                 '/webhooks/workflows/id', '/s/function', '/mcp', '/oauth/token',
                 '/.well-known/oauth-authorization-server', '/open-api/core',
                 '/healthz', '/cloudflare/custom-hostname-webhooks', '/app/billing',
                 '/admin-panel']
        for path in paths:
            response = request(path, 'POST' if path == '/graphql' else 'GET')
            assert json.loads(response.read())['path'] == path
            assert response.headers['Set-Cookie'].startswith('session=smoke;')
            assert received[-1][1]['Host'] == 'sales.example.net'
            assert received[-1][1]['X-Forwarded-Proto'] == 'https'
        try:
            request('/missing.js')
            raise AssertionError('Missing asset returned successful HTML')
        except urllib.error.HTTPError as error:
            assert error.code == 404
        print('PASS: SPA, runtime origin, cache, API paths/query/POST, Host, HTTPS and cookies')
finally:
    subprocess.run(['docker', 'rm', '--force', container], check=False)
    api.shutdown()
