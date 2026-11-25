"""
In-process benchmarks of the Python side of updates to a rendered app.

    python bench_python.py --reps 7 > results_<version>.json

Run it once in each environment. Components are rendered into a Bokeh
Document with server_doc, as they are in a served session, and each
scenario reports the median of its timed operations per repetition.
"""
import argparse
import json
import statistics
import time

import numpy as np
import pandas as pd
import panel as pn

from bokeh.document import Document


def timed(fn, n):
    times = []
    for i in range(n):
        start = time.perf_counter()
        fn(i)
        times.append(time.perf_counter() - start)
    return 1000 * statistics.median(times)


def frame(n, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        'a': rng.random(n),
        'b': rng.integers(0, 1000, n),
        'tag': [f'r{i}' for i in range(n)],
        'when': pd.date_range('2020-01-01', periods=n, freq='min'),
    })


def tabulator_page_change():
    table = pn.widgets.Tabulator(frame(200_000), pagination='remote', page_size=50)
    table.server_doc(Document())
    return timed(lambda i: setattr(table, 'page', i % 100 + 2), 30)


def tabulator_sort():
    table = pn.widgets.Tabulator(frame(200_000), pagination='remote', page_size=50)
    table.server_doc(Document())
    return timed(lambda i: setattr(table, 'sorters', [{'field': 'a', 'dir': 'asc' if i % 2 else 'desc'}]), 10)


def tabulator_patch_sorted():
    table = pn.widgets.Tabulator(frame(200_000), sorters=[{'field': 'a', 'dir': 'asc'}])
    table.server_doc(Document())
    return timed(lambda i: table.patch({'tag': [(3, f'patched{i}')]}), 10)


def tabulator_stream():
    table = pn.widgets.Tabulator(frame(200_000))
    table.server_doc(Document())
    chunk = frame(10, seed=1)
    return timed(lambda i: table.stream(chunk, follow=False), 10)


def _append(layout_cls, child):
    layout = layout_cls(*(child(i) for i in range(2000)))
    layout.server_doc(Document())
    return timed(lambda i: layout.append(child(i)), 20)


def append_classic():
    return _append(pn.Column, lambda i: pn.pane.Markdown(f'Message {i}'))


def append_ui():
    return _append(pn.ui.Column, lambda i: pn.pane.Markdown(f'Message {i}'))


def periodic_markdown_updates():
    """A dashboard of 300 widgets whose Markdown status pane is updated repeatedly."""
    status = pn.pane.Markdown('status')
    app = pn.Column(status, *(pn.widgets.IntSlider(name=f's{i}') for i in range(300)))
    app.server_doc(Document())
    return timed(lambda i: setattr(status, 'object', f'**Status** update {i}'), 200)


def server_doc_classic():
    def run(i):
        pn.Column(*(pn.widgets.IntSlider(name=f's{j}') for j in range(200))).server_doc(Document())
    return timed(run, 5)


def server_doc_ui():
    def run(i):
        pn.ui.Column(*(pn.ui.IntSlider(label=f's{j}') for j in range(200))).server_doc(Document())
    return timed(run, 5)


SCENARIOS = {
    'tabulator_page_change': tabulator_page_change,
    'tabulator_sort': tabulator_sort,
    'tabulator_patch_sorted': tabulator_patch_sorted,
    'tabulator_stream': tabulator_stream,
    'append_classic': append_classic,
    'append_ui': append_ui,
    'markdown_updates': periodic_markdown_updates,
    'server_doc_classic': server_doc_classic,
    'server_doc_ui': server_doc_ui,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reps', type=int, default=7)
    parser.add_argument('--only', default=None)
    args = parser.parse_args()
    names = args.only.split(',') if args.only else list(SCENARIOS)
    # Warm up imports, caches and lazily loaded models once.
    server_doc_ui()
    server_doc_classic()
    results = {name: [] for name in names}
    for _ in range(args.reps):
        for name in names:
            results[name].append(SCENARIOS[name]())
    print(json.dumps({
        'panel': pn.__version__,
        'medians_ms': {k: statistics.median(v) for k, v in results.items()},
        'runs_ms': results,
    }, indent=1))


if __name__ == '__main__':
    main()
