# Reproducing the Lumen 1.4.0 post

- `snippet_*.py` are the code blocks in the post, with the output they printed (`*.out`).
- `charts/make_chart.py` runs one prompt through Lumen with the Claude Code provider and saves the chart
  (Lumen's own PNG export), its Vega-Lite spec and its SQL. `charts/app_ui.py` is the data explorer with a
  hook that saves every finished chart. The `worldmap.*` and `gapminder.*` files are what the two figures
  in the first version of the post were made from; the rebuilt images' specs are written to `charts/ui/`.
- Data: Natural Earth 110m countries,
  <https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson>,
  Vega datasets 2.8.0 `gapminder.json`, and the penguins CSV from `datasets.holoviz.org`.
- A language model wrote each chart, so a rerun gives a different chart.

## Rebuilding the images

```bash
python fetch_data.py            # datasets into charts/data/ (gitignored)
python screenshots.py           # app screenshots and chart exports into ../images/
python illustrations.py         # pipeline.png and collage_1.4.png (run after screenshots.py)
```

`screenshots.py` lists every image's data, prompts, window size and theme in `SHOTS`. It needs
`playwright install chromium` and an LLM: by default it uses OpenAI with `OPENAI_API_KEY` (read from
`~/.zshrc` if the environment lacks it); `LUMEN_BLOG_PROVIDER=claude-code` uses the signed-in `claude` CLI.
Lumen must be at commit 160f2979; `environment.yml` installs it. The report in `report_story.png` uses the
penguins data rather than the original Kaggle music streaming dataset, which needs a Kaggle login. Data sources for the rebuilt images: Our World
in Data's energy dataset (UK electricity) and its `data-centers-share-electricity-demand` chart (IEA and
Ember), EPA AirData `annual_conc_by_monitor_2024` filtered to PM2.5, and Lumen's sample `olympic_medals.csv`.
