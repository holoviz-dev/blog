"""
The two dashboards the served benchmarks use.

Both have the same structure: a sidebar with 40 input widgets, a row of
KPI indicators, a Bokeh line plot, a 1,000 row Tabulator, a Markdown pane
and a "settings" card with another 120 widgets, so roughly 180 components
in total. `classic` is built from the classic widgets in a
FastListTemplate, `ui` from the Material components in `pn.ui.Page`.

Both contain an IntSlider titled "Round trip" whose callback writes the
value into a Markdown pane; bench_server.py uses it to measure the
browser -> Python -> browser round trip.
"""
import numpy as np
import pandas as pd
import panel as pn

from bokeh.plotting import figure

N_ROWS = 1000


def _frame():
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        'station': [f'S{i:04d}' for i in range(N_ROWS)],
        'region': rng.choice(['North', 'South', 'East', 'West'], N_ROWS),
        'output_mw': rng.random(N_ROWS) * 20,
        'capacity_mw': rng.random(N_ROWS) * 30,
        'online': rng.random(N_ROWS) > 0.2,
    })


def _plot():
    x = np.arange(500)
    p = figure(height=300, sizing_mode='stretch_width', title='Output')
    p.line(x, np.cumsum(np.random.default_rng(1).normal(size=500)))
    return p


def classic():
    w = pn.widgets
    sidebar = []
    for i in range(10):
        sidebar += [
            w.IntSlider(name=f'Slider {i}', start=0, end=100, value=i),
            w.Select(name=f'Select {i}', options=['a', 'b', 'c']),
            w.Checkbox(name=f'Check {i}'),
            w.TextInput(name=f'Text {i}', value=f'value {i}'),
        ]
    settings = [w.FloatSlider(name=f'Setting {i}', start=0, end=1, step=0.01) for i in range(60)]
    settings += [w.Switch(name=f'Flag {i}') for i in range(60)]

    rt = w.IntSlider(name='Round trip', start=0, end=10_000, value=0)
    out = pn.pane.Markdown('rt-value: 0')
    rt.param.watch(lambda e: setattr(out, 'object', f'rt-value: {e.new}'), 'value')

    kpis = pn.Row(*(pn.indicators.Number(name=f'KPI {i}', value=i * 10, format='{value} MW') for i in range(4)))
    return pn.template.FastListTemplate(
        title='Classic dashboard',
        sidebar=sidebar,
        main=[
            kpis,
            pn.pane.Bokeh(_plot(), sizing_mode='stretch_width'),
            pn.widgets.Tabulator(_frame(), pagination='local', page_size=20, sizing_mode='stretch_width'),
            pn.pane.Markdown('## Notes\n\nThis dashboard is used to benchmark Panel. Dashboard ready.'),
            pn.Row(rt, out),
            pn.Card(pn.FlexBox(*settings), title='Settings', collapsed=False),
        ],
    )


def ui():
    u = pn.ui
    sidebar = []
    for i in range(10):
        sidebar += [
            u.IntSlider(label=f'Slider {i}', start=0, end=100, value=i),
            u.Select(label=f'Select {i}', options=['a', 'b', 'c']),
            u.Checkbox(label=f'Check {i}'),
            u.TextInput(label=f'Text {i}', value=f'value {i}'),
        ]
    settings = [u.FloatSlider(label=f'Setting {i}', start=0, end=1, step=0.01) for i in range(60)]
    settings += [u.Switch(label=f'Flag {i}') for i in range(60)]

    # The round trip uses a classic slider and Markdown pane in both apps,
    # so the measurement finds the same Bokeh models in the browser.
    rt = pn.widgets.IntSlider(name='Round trip', start=0, end=10_000, value=0)
    out = pn.pane.Markdown('rt-value: 0')
    rt.param.watch(lambda e: setattr(out, 'object', f'rt-value: {e.new}'), 'value')

    kpis = u.Row(*(pn.indicators.Number(name=f'KPI {i}', value=i * 10, format='{value} MW') for i in range(4)))
    return u.Page(
        title='Material dashboard',
        sidebar=sidebar,
        main=[
            kpis,
            pn.pane.Bokeh(_plot(), sizing_mode='stretch_width'),
            pn.widgets.Tabulator(_frame(), pagination='local', page_size=20, sizing_mode='stretch_width'),
            pn.pane.Markdown('## Notes\n\nThis dashboard is used to benchmark Panel. Dashboard ready.'),
            u.Row(rt, out),
            u.Card(u.Column(*settings), title='Settings'),
        ],
    )


APPS = {'classic': classic, 'ui': ui}
