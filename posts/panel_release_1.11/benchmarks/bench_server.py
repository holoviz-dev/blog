"""
Served-app benchmarks: session creation over HTTP, page loads in Chromium
and the browser -> Python -> browser round trip.

    python bench_server.py --env 1.10=/path/to/env110/bin/python \
                           --env 1.11=/path/to/env111/bin/python \
                           --reps 5 --out results_server.json

Each --env is the Python of an environment with the Panel version to test;
it is only used to run serve.py. This script itself needs playwright (with
Chromium installed) and tornado. Versions are interleaved within each
repetition, and every repetition starts a fresh server. --browser-only skips
the HTTP session benchmarks and only measures page loads and round trips.
"""
import argparse
import asyncio
import json
import os
import pathlib
import socket
import statistics
import subprocess
import time

from concurrent.futures import ThreadPoolExecutor

from playwright.sync_api import sync_playwright
from tornado.httpclient import AsyncHTTPClient

HERE = pathlib.Path(__file__).parent

ROUND_TRIP_JS = """
async (k) => {
  const doc = Bokeh.documents[0]
  const models = [...doc.all_models]
  const slider = models.find(m => m.type === 'Slider' && m.title === 'Round trip')
  const md = models.find(m => typeof m.text === 'string' && m.text.includes('rt-value'))
  const target = new RegExp(`rt-value: ${k}\\\\b`)
  return await new Promise(resolve => {
    const done = () => {
      if (target.test(md.text)) {
        md.properties.text.change.disconnect(done)
        resolve(performance.now() - t0)
      }
    }
    md.properties.text.change.connect(done)
    const t0 = performance.now()
    slider.value = k
  })
}
"""

IDLE_JS = """
() => (window.Bokeh && Bokeh.documents.length && Bokeh.documents[0].is_idle) ? performance.now() : false
"""


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class Server:

    def __init__(self, python, app):
        self.port = free_port()
        self.url = f'http://localhost:{self.port}/{app}'
        self.proc = subprocess.Popen(
            [python, str(HERE / 'serve.py'), app, str(self.port)], cwd=HERE,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self._wait()

    def _wait(self, timeout=60):
        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.create_connection(('127.0.0.1', self.port), timeout=1):
                    return
            except OSError:
                time.sleep(0.2)
        raise RuntimeError('Server did not start')

    def stop(self):
        self.proc.terminate()
        self.proc.wait()


async def _get(client, url):
    start = time.perf_counter()
    await client.fetch(url, request_timeout=120)
    return time.perf_counter() - start


async def http_bench(url, n_seq=20, n_conc=40, concurrency=8):
    AsyncHTTPClient.configure(None, max_clients=concurrency)
    client = AsyncHTTPClient()
    for _ in range(3):
        await _get(client, url)
    seq = [await _get(client, url) for _ in range(n_seq)]
    start = time.perf_counter()
    await asyncio.gather(*(_get(client, url) for _ in range(n_conc)))
    wall = time.perf_counter() - start
    client.close()
    return {'session_ms': 1000 * statistics.median(seq), 'throughput_rps': n_conc / wall}


def load_page(context, url):
    page = context.new_page()
    cdp = context.new_cdp_session(page)
    cdp.send('Network.enable')
    stats = {'wire': 0, 'decoded': 0, 'requests': 0}

    def finished(params):
        stats['wire'] += params['encodedDataLength']
        stats['requests'] += 1

    def received(params):
        stats['decoded'] += params['dataLength']

    cdp.on('Network.loadingFinished', finished)
    cdp.on('Network.dataReceived', received)
    page.goto(url, wait_until='commit')
    idle = page.wait_for_function(IDLE_JS, polling='raf', timeout=60_000).json_value()
    page.wait_for_timeout(500)
    return page, {'idle_ms': idle, 'wire_kb': stats['wire'] / 1024,
                  'decoded_kb': stats['decoded'] / 1024, 'requests': stats['requests']}


def browser_bench(browser, url, n_cold=3, n_rt=40):
    cold, warm = [], []
    rt = []
    for _ in range(n_cold):
        context = browser.new_context(viewport={'width': 1400, 'height': 900})
        page, stats = load_page(context, url)
        cold.append(stats)
        page.close()
        page, stats = load_page(context, url)
        warm.append(stats)
        if not rt:
            # The first few updates warm up the server, so they are discarded.
            rt = [page.evaluate(ROUND_TRIP_JS, k) for k in range(1, n_rt + 6)][5:]
        context.close()

    def med(rows, key):
        return statistics.median(r[key] for r in rows)

    return {
        'cold_idle_ms': med(cold, 'idle_ms'), 'cold_wire_kb': med(cold, 'wire_kb'),
        'cold_decoded_kb': med(cold, 'decoded_kb'), 'cold_requests': med(cold, 'requests'),
        'warm_idle_ms': med(warm, 'idle_ms'), 'warm_wire_kb': med(warm, 'wire_kb'),
        'warm_requests': med(warm, 'requests'),
        'round_trip_ms': statistics.median(rt),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', action='append', required=True, help='label=/path/to/python')
    parser.add_argument('--apps', default='classic,ui')
    parser.add_argument('--reps', type=int, default=5)
    parser.add_argument('--out', default='results_server.json')
    parser.add_argument('--browser-only', action='store_true')
    args = parser.parse_args()
    envs = dict(e.split('=', 1) for e in args.env)

    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for rep in range(args.reps):
            for app in args.apps.split(','):
                for label, python in envs.items():
                    server = Server(python, app)
                    try:
                        row = {'rep': rep, 'app': app, 'version': label}
                        if not args.browser_only:
                            # The sync Playwright API owns an event loop on this thread.
                            with ThreadPoolExecutor(1) as ex:
                                row.update(ex.submit(asyncio.run, http_bench(server.url)).result())
                        row.update(browser_bench(browser, server.url))
                    finally:
                        server.stop()
                    print(json.dumps(row), flush=True)
                    results.append(row)
                    with open(args.out, 'w') as f:
                        json.dump(results, f, indent=1)
        browser.close()


if __name__ == '__main__':
    os.environ.setdefault('PYTHONUNBUFFERED', '1')
    main()
