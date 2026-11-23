"""
Summarise the results and draw the chart used in the post.

    python report.py   # reads results_*.json, writes ../images/perf_1.11.png

Three environments are compared: Panel 1.10 ("1.10", with param 2.4 and
panel-material-ui 0.16), Panel 1.11 with the same param and
panel-material-ui ("1.11-base") and Panel 1.11 with param 2.5 and
panel-material-ui 0.17 ("1.11").
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


VERSIONS = [('1.10', '110'), ('1.11-base', '111base'), ('1.11', '111')]


def main():
    rows = json.loads((HERE / 'results_server.json').read_text())
    py = {tag: json.loads((HERE / f'results_python_{tag}.json').read_text())['medians_ms'] for _, tag in VERSIONS}
    table = []
    for app, key, label, higher in SERVER:
        values = [
            statistics.median(r[key] for r in rows if r['app'] == app and r['version'] == version)
            for version, _ in VERSIONS
        ]
        table.append((label, values, higher))
    for key, label in PYTHON:
        table.append((label, [py[tag][key] for _, tag in VERSIONS], False))
    print(f'{"":58s} {"1.10":>10s} {"1.11 base":>10s} {"1.11":>10s} {"base":>7s} {"full":>7s}')
    for label, values, higher in table:
        old = values[0]
        speedups = [v / old if higher else old / v for v in values[1:]]
        print(f'{label:58s} ' + ' '.join(f'{v:10.2f}' for v in values) + ' ' + ' '.join(f'{x:6.1f}x' for x in speedups))
    return table


def speedups(table):
    out = {}
    for label, values, higher in table:
        old = values[0]
        out[label] = [v / old if higher else old / v for v in values[1:]]
    return out


def chart(entries, path):
    """entries: list of (label, (base_speedup, full_speedup)), drawn top to bottom."""
    surface, ink, muted = '#fcfcfb', '#0b0b0b', '#52514e'
    colors = ('#9bbfea', '#2a78d6')
    names = ('Panel 1.11 with param 2.4 and panel-material-ui 0.16',
             'Panel 1.11 with param 2.5 and panel-material-ui 0.17')
    labels = [e[0] for e in entries][::-1]
    pairs = [e[1] for e in entries][::-1]
    top = max(max(p) for p in pairs)
    fig, ax = plt.subplots(figsize=(8, 0.62 * len(entries) + 1.4), dpi=200)
    fig.patch.set_facecolor(surface)
    ax.set_facecolor(surface)
    height = 0.36
    for i, (color, name) in enumerate(zip(colors, names)):
        ys = [y + (i - 0.5) * height for y in range(len(labels))]
        values = [p[i] for p in pairs]
        bars = ax.barh(ys, values, height=height * 0.92, color=color, label=name)
        for bar, v in zip(bars, values):
            ax.text(bar.get_width() + top * 0.01, bar.get_y() + bar.get_height() / 2,
                    f'{v:.1f}×', va='center', ha='left', fontsize=8, color=ink)
    ax.set_yticks(range(len(labels)), labels)
    ax.axvline(1, color=muted, lw=0.8, ls=(0, (3, 3)))
    ax.set_xlim(0, top * 1.14)
    ax.set_xlabel('Times faster (or smaller) than Panel 1.10, dashed line = no change', color=muted, fontsize=9)
    ax.tick_params(axis='y', length=0, labelsize=9, labelcolor=ink)
    ax.tick_params(axis='x', labelsize=8, colors=muted)
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color(muted)
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1.0), frameon=False, fontsize=8, labelcolor=ink)
    fig.tight_layout()
    fig.savefig(path, facecolor=surface)


CHART = [
    'Page load, bytes on the wire (FastListTemplate)',
    'Page load, bytes on the wire (pn.ui.Page)',
    'Session creation (FastListTemplate)',
    'Session creation (pn.ui.Page)',
    'Render a pn.ui.Column of 200 widgets',
    'Browser to Python to browser (FastListTemplate)',
    'Browser to Python to browser (pn.ui.Page)',
    'Append to a Column of 2,000 items',
    'Tabulator page change, 200k rows',
    'Tabulator sort, 200k rows',
]


if __name__ == '__main__':
    table = speedups(main())
    chart([(label, table[label]) for label in CHART], HERE.parent / 'images' / 'perf_1.11.png')
