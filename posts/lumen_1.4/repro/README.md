# Reproducing the Lumen 1.4.0 post

- `snippet_*.py` are the code blocks in the post, with the output they printed (`*.out`).
- `charts/make_chart.py` runs one prompt through Lumen with the Claude Code provider and saves the chart
  (Lumen's own PNG export), its Vega-Lite spec and its SQL. `charts/app_ui.py` is the data explorer with a
  hook that saves every finished chart. The `worldmap.*` and `gapminder.*` files are what the two figures
  were made from.
- Data: Natural Earth 110m countries,
  <https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson>,
  Vega datasets 2.8.0 `gapminder.json`, and the penguins CSV from `datasets.holoviz.org`.
- A language model wrote each chart, so a rerun gives a different chart.
