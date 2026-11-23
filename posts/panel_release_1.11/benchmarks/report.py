"""
Summarise the results and draw the chart used in the post.

    python report.py   # reads results_*.json, writes ../images/perf_1.11.png
"""
import json
import pathlib
import statistics

import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).parent

SERVER = [
    # (app, key, label, higher_is_better)
    ('classic', 'cold_wire_kb', 'Page load, bytes on the wire (FastListTemplate)', False),
    ('ui', 'cold_wire_kb', 'Page load, bytes on the wire (pn.ui.Page)', False),
    ('classic', 'cold_idle_ms', 'Page load to rendered (FastListTemplate)', False),
    ('ui', 'cold_idle_ms', 'Page load to rendered (pn.ui.Page)', False),
    ('classic', 'session_ms', 'Session creation (FastListTemplate)', False),
    ('ui', 'session_ms', 'Session creation (pn.ui.Page)', False),
    ('classic', 'throughput_rps', 'Sessions per second, 8 concurrent (FastListTemplate)', True),
    ('ui', 'throughput_rps', 'Sessions per second, 8 concurrent (pn.ui.Page)', True),
    ('classic', 'round_trip_ms', 'Browser to Python to browser (FastListTemplate)', False),
    ('ui', 'round_trip_ms', 'Browser to Python to browser (pn.ui.Page)', False),
]

PYTHON = [
    ('server_doc_classic', 'Render a Column of 200 widgets'),
    ('server_doc_ui', 'Render a pn.ui.Column of 200 widgets'),
    ('append_classic', 'Append to a Column of 2,000 items'),
    ('append_ui', 'Append to a pn.ui.Column of 2,000 items'),
    ('tabulator_page_change', 'Tabulator page change, 200k rows'),
    ('tabulator_sort', 'Tabulator sort, 200k rows'),
    ('tabulator_patch_sorted', 'Tabulator patch with a sorter, 200k rows'),
    ('tabulator_stream', 'Tabulator stream 10 rows, 200k rows'),
    ('markdown_updates', 'Markdown update in a 300 widget app'),
]


def main():
    rows = json.loads((HERE / 'results_server.json').read_text())
    py = {v: json.loads((HERE / f'results_python_{v}.json').read_text())['medians_ms'] for v in ('110', '111')}
    table = []
    for app, key, label, higher in SERVER:
        old = statistics.median(r[key] for r in rows if r['app'] == app and r['version'] == '1.10')
        new = statistics.median(r[key] for r in rows if r['app'] == app and r['version'] == '1.11')
        table.append((label, old, new, new / old if higher else old / new))
    for key, label in PYTHON:
        old, new = py['110'][key], py['111'][key]
        table.append((label, old, new, old / new))
    for label, old, new, speedup in table:
        print(f'{label:58s} {old:10.2f} {new:10.2f} {speedup:6.1f}x')
    return table


def chart(entries, path):
    """entries: list of (label, speedup), drawn top to bottom."""
    surface, ink, muted, series = '#fcfcfb', '#0b0b0b', '#52514e', '#2a78d6'
    labels = [e[0] for e in entries][::-1]
    values = [e[1] for e in entries][::-1]
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(entries) + 1.1), dpi=200)
    fig.patch.set_facecolor(surface)
    ax.set_facecolor(surface)
    bars = ax.barh(labels, values, height=0.6, color=series)
    for bar, v in zip(bars, values):
        ax.text(bar.get_width() + max(values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f'{v:.1f}×', va='center', ha='left', fontsize=9, color=ink)
    ax.axvline(1, color=muted, lw=0.8, ls=(0, (3, 3)))
    ax.set_xlim(0, max(values) * 1.12)
    ax.set_xlabel('Times faster (or smaller) in Panel 1.11 than in 1.10, dashed line = no change', color=muted, fontsize=9)
    ax.tick_params(axis='y', length=0, labelsize=9, labelcolor=ink)
    ax.tick_params(axis='x', labelsize=8, colors=muted)
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color(muted)
    fig.tight_layout()
    fig.savefig(path, facecolor=surface)


CHART = [
    'Page load, bytes on the wire (FastListTemplate)',
    'Page load, bytes on the wire (pn.ui.Page)',
    'Session creation (FastListTemplate)',
    'Session creation (pn.ui.Page)',
    'Browser to Python to browser (FastListTemplate)',
    'Browser to Python to browser (pn.ui.Page)',
    'Append to a Column of 2,000 items',
    'Tabulator page change, 200k rows',
    'Tabulator sort, 200k rows',
]


if __name__ == '__main__':
    table = {label: speedup for label, _, _, speedup in main()}
    chart([(label, table[label]) for label in CHART], HERE.parent / 'images' / 'perf_1.11.png')
