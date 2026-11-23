---
title: "Panel 1.11.0 Release"
date: "YYYY-MM-DD"
description: "Release announcement for Panel 1.11"
author: "Philipp Rudiger"
categories: [release, panel]
image: "images/collage_1.11.png"
aliases:
  - ../../panel_1.11.html
---

<!-- EDITOR: Set the date above. images/collage_1.11.png is a placeholder made by tiling example screenshots; replace it with a proper collage. -->

<img src="./images/collage_1.11.png" width="100%"></img>

## What is Panel?

[Panel](https://panel.holoviz.org/) is an open-source Python library for building tools, dashboards and complex applications entirely in Python. It comes with the PyData ecosystem, advanced data tables and much more built in, and offers both high-level reactive APIs and lower-level callback-based APIs, so you can put together an exploratory app in a few lines or develop a multi-page application with rich interactivity. Panel is a member of the [HoloViz](https://holoviz.org) ecosystem, alongside a suite of tools designed for data exploration.

## New Release!

We are happy to announce the 1.11.0 release of Panel! Panel 1.10 changed how you build Panel apps with `pn.ui`. This release makes those apps, and the classic ones, faster. We spent a large part of the cycle profiling real applications and removing fixed costs from every page load, session, component and event, The same app, unchanged, now loads a fraction of the bytes, starts sessions faster and answers events in a third of the time or less. `Tabulator` and the other data components now also work with Polars, PyArrow and other DataFrame libraries, which let us make pandas an optional dependency, and the release fixes a long list of bugs, including several affecting authentication and apps deployed behind a reverse proxy.

Many thanks to the contributors to this release: [@philippjfr](https://github.com/philippjfr), [@hoxbro](https://github.com/hoxbro), [@maximlt](https://github.com/maximlt), [@aarab-malik](https://github.com/aarab-malik), [@AaryanRS](https://github.com/AaryanRS), [@benjibunbun](https://github.com/benjibunbun), [@Cherith1222](https://github.com/Cherith1222), [@chiruu12](https://github.com/chiruu12), [@Jojoussef](https://github.com/Jojoussef), [@SAMARTHJAISWAL](https://github.com/SAMARTHJAISWAL), [@Web4everyone32](https://github.com/Web4everyone32), [@YashAnand69](https://github.com/YashAnand69), [@Adithya6721](https://github.com/Adithya6721), [@Adititodekar](https://github.com/Adititodekar), [@ahuang11](https://github.com/ahuang11), [@Alpenj](https://github.com/Alpenj), [@compiler-segfault](https://github.com/compiler-segfault), [@JoeyTan21](https://github.com/JoeyTan21), [@Kkkakania](https://github.com/Kkkakania), [@MarcSkovMadsen](https://github.com/MarcSkovMadsen), [@mmporong](https://github.com/mmporong), [@nightcityblade](https://github.com/nightcityblade), [@nojaf](https://github.com/nojaf), [@ryandesign](https://github.com/ryandesign), [@SuMayaBee](https://github.com/SuMayaBee), [@sushan5140](https://github.com/sushan5140) and [@tmichela](https://github.com/tmichela).

<hr>

If you're using [Anaconda](https://www.anaconda.com/downloads), you can install the latest version of Panel with `conda install panel`. If you prefer pip, use `pip install panel`. Note that pip no longer installs pandas for you; use `pip install "panel[recommended]"` if you want it.

<hr>

## Performance

Panel 1.11 removes a lot of fixed cost from serving an app: in the bytes a page loads, in the work done for each session and component, and in the overhead around each event. You get all of it without changing any code.

To see what that means for a real app, we built the same dashboard twice, once from classic components in a `FastListTemplate` and once from Material components in a `pn.ui.Page`. Each has around 180 components: 40 widgets in the sidebar, a row of indicators, a Bokeh plot, a 1,000 row `Tabulator`, some Markdown and a card with 120 more widgets. We served both with Panel 1.10.0 and 1.11.0rc0 and measured them in headless Chromium, alongside a few Python-side scenarios around large layouts and tables.

<img src="./images/perf_1.11.png" width="100%"></img>

| Scenario | 1.10.0 | 1.11.0rc0 | Change |
|---|---|---|---|
| Data transferred on first page load, classic | 5.5 MB | 1.0 MB | 5.4× less |
| Data transferred on first page load, Material | 5.0 MB | 1.5 MB | 3.2× less |
| First page load until rendered, classic | 748 ms | 624 ms | 1.2× |
| First page load until rendered, Material | 977 ms | 647 ms | 1.5× |
| Creating a session, classic | 311 ms | 224 ms | 1.4× |
| Creating a session, Material | 333 ms | 114 ms | 2.9× |
| Sessions per second with 8 concurrent requests, Material | 2.8 | 8.4 | 3.0× |
| Browser to Python to browser round trip, classic | 79 ms | 28 ms | 2.9× |
| Browser to Python to browser round trip, Material | 425 ms | 32 ms | 13× |
| Appending to a `Column` of 2,000 items | 74 ms | 5.5 ms | 13× |
| Changing the page of a 200,000 row `Tabulator` (remote pagination) | 8.8 ms | 0.36 ms | 24× |
| Sorting a 200,000 row `Tabulator` | 65 ms | 19 ms | 3.4× |
| Patching a cell of a sorted 200,000 row `Tabulator` | 65 ms | 18 ms | 3.6× |

The biggest change on page load is the amount of data. MathJax used to be loaded by every template page and is now only loaded when a page contains math, templates no longer load their resources twice, and responses are gzipped ([#9058](https://github.com/holoviz/panel/pull/9058)). Our benchmark runs on localhost, so it barely shows in the load time, but over a real network the drop from 5.5 MB to 1 MB matters much more. Versioned resources also get long-lived cache headers, so the browser reuses them without asking the server again.

Creating a session is where every user waits before seeing anything, and it also limits how many users a single server process can handle. Caching the per-request resource bookkeeping ([#9068](https://github.com/holoviz/panel/pull/9068)), cheaper Bokeh model creation ([#9064](https://github.com/holoviz/panel/pull/9064)) and cheaper component construction ([#9069](https://github.com/holoviz/panel/pull/9069)) speed up every app. Material components benefit most, because `JSComponent` and `ReactComponent` now compute their per-class information once instead of for every instance and skip properties that are still at their defaults ([#9067](https://github.com/holoviz/panel/pull/9067), [#9095](https://github.com/holoviz/panel/pull/9095)). That roughly triples how many Material sessions a server can create per second.

The round trip measures how long it takes from a change in the browser until the update made by a Python callback arrives back. In 1.10 every event on the Material page cost more than 400 ms; in 1.11 it costs about the same as on the classic page. Busy-state bookkeeping and in-place pane updates got much cheaper, and Panel now waits 20 ms instead of 50 ms for further changes before processing an event from the browser ([#9066](https://github.com/holoviz/panel/pull/9066)). Appending to or replacing children of a large layout, which chat apps and logs do all the time, no longer scales with the number of children already there ([#9057](https://github.com/holoviz/panel/pull/9057)), and `Tabulator` updates on large tables no longer reprocess or resend the whole table ([#9071](https://github.com/holoviz/panel/pull/9071)). In the browser, `Tabulator` now applies `stream`, `patch` and selection changes to the existing table instead of rebuilding it ([#9065](https://github.com/holoviz/panel/pull/9065)).

A few other improvements are not in the table: `pn.cache` hits are more than ten times cheaper ([#9063](https://github.com/holoviz/panel/pull/9063)), `Vega` and `Plotly` panes avoid redundant re-renders ([#9061](https://github.com/holoviz/panel/pull/9061)), and Documents cleaned up without a session, such as those created by health checks, no longer stay in memory forever ([#9059](https://github.com/holoviz/panel/pull/9059)).

All numbers are medians over 5 runs of the served benchmarks (each on a fresh server, with the 40 round trips in each run also reduced to their median) and 7 runs of the Python-side ones. We ran them on an Apple M5 Pro with Python 3.14.4 and Bokeh 3.10.2, comparing Panel 1.10.0 with panel-material-ui 0.16.7 against Panel 1.11.0rc0 with panel-material-ui 0.17.0rc0. Most of the Material gains come from Panel itself: with the older panel-material-ui, 1.11 still creates the Material session in 124 ms and completes the round trip in 45 ms. The scripts are in the [`benchmarks`](https://github.com/holoviz-dev/blog/tree/main/posts/panel_release_1.11/benchmarks) folder next to this post if you want to reproduce them.

<!-- EDITOR: Check the benchmarks link above points at where this post's folder ends up in the blog repo. Re-run the benchmarks against 1.11.0 final if anything performance-related lands after rc0. -->

## Any DataFrame, and optional pandas

Panel 1.10 taught the `DataFrame` pane to render any DataFrame supported by [Narwhals](https://narwhals-dev.github.io/narwhals/). In 1.11 the interactive data components follow: `Tabulator`, the `DataFrame` widget, `Perspective` and `Vizzu` accept Polars, PyArrow and any other eager DataFrame Narwhals supports, without converting it to pandas ([#8841](https://github.com/holoviz/panel/pull/8841)). Filtering, sorting, remote pagination, selection, edits, `stream()` and `patch()` all work, and `.value` stays the type you passed in:

```python
import panel as pn
import polars as pl

df = pl.DataFrame({
    'station': ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot'],
    'region': ['North', 'South', 'North', 'East', 'West', 'South'],
    'output_mw': [12.4, 8.1, 15.0, 9.7, 11.2, 6.3],
    'online': [True, True, False, True, True, False],
})

table = pn.ui.Tabulator(
    df,
    header_filters=True,
    sorters=[{'field': 'output_mw', 'dir': 'desc'}],
    layout='fit_columns',
    sizing_mode='stretch_width',
)

total = pn.ui.Typography(variant='h6')

def update_total(event=None):
    total.object = f"Total output: {table.value['output_mw'].sum():.1f} MW ({type(table.value).__module__.split('.')[0]})"

table.on_edit(update_total)
update_total()

pn.ui.Page(title='Polars in Tabulator', main=[total, table]).servable()
```

<img src="./images/polars_tabulator.png" width="80%"></img>

*After editing Alpha's output to 20, the total is recomputed from the Polars frame.*

Since these frames have no index, rows are addressed by position, and `Styler` based styling remains pandas-only; the [Tabulator reference](https://panel.holoviz.org/en/docs/latest/reference/widgets/Tabulator.html) has the details. With nothing in Panel's core depending on pandas any more, it has moved to the `recommended` extra, as announced in the 1.9 release notes. If your app uses pandas, make sure it is in your own requirements.

## Bug fixes

This release contains around a hundred bug fixes. Two groups deserve a mention because they affect how apps are deployed.

Authentication got several fixes. The login redirect validation now rejects `next` values such as `///evil.com`, which browsers resolve to another site, closing an open redirect in both the basic auth and OAuth login flows ([#8938](https://github.com/holoviz/panel/pull/8938)); we recommend upgrading if you use authentication. OAuth behind a reverse proxy or with `--prefix` used to need a hand-written `--oauth-redirect-uri`, and some setups did not work at all. Panel now derives the external URL from the request, `--root-path`, `--prefix` and, with `--use-xheaders`, the `X-Forwarded-Host` and `X-Forwarded-Prefix` headers, and uses it for the redirect URI and every login and logout redirect ([#9072](https://github.com/holoviz/panel/pull/9072), building on [#8211](https://github.com/holoviz/panel/pull/8211) by [@TheoMathurin](https://github.com/TheoMathurin)). `--oauth-guest-endpoints` entries ending in `/*` now cover the paths below them, so a branded login page can load its assets ([#9033](https://github.com/holoviz/panel/pull/9033)), and Panel warns when the session token gets close to the 8 KB header limit of common proxies, which otherwise surfaced only as "Could not open websocket" in the browser ([#8638](https://github.com/holoviz/panel/pull/8638)).

Resource loading behind proxies and on nested routes is also fixed. Stylesheets defined relative to a design or theme were cached with the URL of whichever route rendered them first, so a page on a nested route such as `/dash/<id>` requested them from the wrong place and got a 404. Lazily loaded resources had the same problem after navigating within an app under `panel serve`. Both now resolve against the route the session is on, including behind a proxy that strips its prefix ([#9109](https://github.com/holoviz/panel/pull/9109)). Hosts that rewrite or do not serve Panel's `static/extensions/` routes, such as Shiny, now load components too, falling back to the CDN when a resource request fails ([#9020](https://github.com/holoviz/panel/pull/9020)).

<!-- EDITOR: #9109 was merged after v1.11.0rc0 and has no entry in the release notes yet; drop the paragraph above to its last sentence if it does not ship in 1.11.0. -->

Beyond those, threaded apps no longer hit races on the document lock, updates made inside a long running synchronous callback reach the browser while it runs again, notebooks sync every change of a message, and `Tabulator`, `Plotly`, `FloatPanel`, `Tabs` and the classic templates received many smaller fixes. The changelog below has the full list.

## Upgrading

A few changes may need your attention. `pip install panel` no longer installs pandas. The default OAuth redirect URI now includes `--prefix` and follows the forwarded headers with `--use-xheaders`, so you may have to register the new URI with your provider or pass the old one with `--oauth-redirect-uri`. Responses are now gzipped (turn it off with `pn.serve(..., compress=False)` if your proxy already compresses), and changes from the browser are debounced for 20 ms instead of 50 ms. The [upgrade guide](https://panel.holoviz.org/en/docs/latest/upgrade.html) and the behaviour change markers in the changelog cover the rest.

## Panel and AI

The chat components benefit from the performance work, and streaming text with math into a `Markdown` pane now typesets only the blocks that changed ([#9061](https://github.com/holoviz/panel/pull/9061)). `ChatInterface` gained a `widget_placeholder` parameter ([#9040](https://github.com/holoviz/panel/pull/9040)). If you use an AI coding assistant to write Panel code, point it at our [`llms.txt`](https://panel.holoviz.org/en/docs/latest/llms.txt), which indexes Markdown versions of every documentation page, or install the [HoloViz Agent Skills](https://skills.holoviz.org/) with `uvx holoviz-skills@latest install`. The guide on [using Panel with an AI assistant](https://panel.holoviz.org/en/docs/latest/how_to/use_llms.html) covers both.

## What comes next

We now have benchmarks for page loads, sessions, components, layouts, `Tabulator` and caching, so we can keep measuring as we go, and we will keep chipping away at the remaining costs. Panel 2.0, where the Material components become the default, stays the larger goal. If you have questions or want to share what you built, join us on [Discourse](https://discourse.holoviz.org/) or [Discord](https://discord.gg/AXRHnJU6sP), and please report bugs and ideas on [GitHub](https://github.com/holoviz/panel/issues).

## Changelog

For the full list of changes, see the [Panel 1.11.0 changelog](https://github.com/holoviz/panel/releases/tag/v1.11.0).

<!-- EDITOR: The list below is the 1.11.0 section of doc/about/releases.md as of v1.11.0rc0; refresh it from the final release notes. -->

### 🚀 Features

* Accept Polars, PyArrow and any other eager DataFrame supported by Narwhals in `Tabulator`, the `DataFrame` widget, `Perspective` and `Vizzu` without converting it to pandas. Filtering, sorting, remote pagination, selection, edits, `stream()` and `patch()` all work on these frames, with rows addressed by position since they have no index, and PyArrow tables keep `large_string` and other large column types when they are edited, patched or streamed into ([#8841](https://github.com/holoviz/panel/pull/8841), [#9086](https://github.com/holoviz/panel/pull/9086))

### ✨ Enhancements

* Show a default `Filter by <column>...` placeholder in `Tabulator` header filters ([#8452](https://github.com/holoviz/panel/pull/8452))
* Add a `widget_placeholder` parameter to `ChatInterface` that sets, and later updates, the placeholder of its default input widget ([#9040](https://github.com/holoviz/panel/pull/9040))
* Add `max_completions` to `AutocompleteInput` to limit the number of suggestions shown ([#9031](https://github.com/holoviz/panel/pull/9031))
* Let `save` export PNGs with Bokeh's Playwright backend, selected with the new `backend` argument (e.g. `.save('x.png', backend='playwright')`) or `BOKEH_EXPORT_BACKEND`, and apply Panel's page template and idle wait to screenshots again on Bokeh 3.10 ([#8918](https://github.com/holoviz/panel/pull/8918))
* Add a `compress` option to `pn.serve` and `get_server` (default `True`) to turn off response compression, for example behind a proxy that already compresses ([#9058](https://github.com/holoviz/panel/pull/9058))
* Let `--oauth-guest-endpoints` entries ending in `/*` or `/` cover the paths below them, so e.g. a branded login page can load its logo from `--static-dirs`; plain entries now match the path without the query string but still do not cover sub-paths ([#9033](https://github.com/holoviz/panel/pull/9033))
* Log a one-time warning per app when the Bokeh session token approaches the 8 KB request header limit of common proxies, which otherwise fails with an unexplained "Could not open websocket" ([#8638](https://github.com/holoviz/panel/pull/8638))
* Load the `TextEditor` (Quill) resources from the CDN configured with `PANEL_NPM_CDN` instead of always from jsDelivr ([#7826](https://github.com/holoviz/panel/pull/7826))

### ⚡ Performance

This release removes much of the fixed cost of serving a Panel app, from the bytes a page loads to the work done per session, per component and per event. The numbers below are the ones measured in each pull request.

* Load fewer resources per page and serve them compressed and cached. MathJax is only loaded on pages that contain math, template resources are no longer loaded twice, responses are gzipped, static files are compressed once and versioned resources get long-lived cache headers. A `FastListTemplate` page went from 5831 KB to 3143 KB of local resources, 830 KB on the wire ([#9058](https://github.com/holoviz/panel/pull/9058))
* Cache the per-request resource bookkeeping, apply a template's design once and stop streaming log records into the admin dashboard when nobody is looking; generating the page for a 200-widget app went from 16.1 ms to 1.3 ms ([#9068](https://github.com/holoviz/panel/pull/9068))
* Speed up Bokeh model creation in `server_doc`; a `Column` of 200 widgets went from 173 ms to 104 ms ([#9064](https://github.com/holoviz/panel/pull/9064))
* Cut the cost of constructing Panel components and of `pn.panel` dispatch; a `Column` of 20 sliders is 47% cheaper to create and `pn.panel('text')` 42% cheaper ([#9069](https://github.com/holoviz/panel/pull/9069))
* Make `JSComponent` and `ReactComponent`, and with them every `panel-material-ui` component, cheap to render and update; `server_doc` of a `ui.Column` of 200 widgets went from 534 ms to 335 ms and appending to a `ui.Column(2000)` from 167 ms to 13.7 ms ([#9067](https://github.com/holoviz/panel/pull/9067), [#9099](https://github.com/holoviz/panel/pull/9099))
* Further reduce the cost of creating `ReactiveESM` models, such as those of `panel-material-ui` components, by dropping default-valued properties when constructing the model and its DataModel, narrowing the reference scan of DataModel properties, registering event callbacks without a per-callback signature inspection and reusing the Document's shared stylesheets instead of building a throwaway per component; `server_doc` of a `ui.Column` of 200 components went from 124 ms to 86 ms with an unchanged serialized Document ([#9095](https://github.com/holoviz/panel/pull/9095))
* Send a compiled inline ESM bundle once per document instead of once per component, so ten `panel-material-ui` buttons in a notebook or exported HTML file go from 15 MB to 1.7 MB ([#9104](https://github.com/holoviz/panel/pull/9104))
* Make mutations of large layouts cheap; appending to a `Column` with 2000 children went from 89.1 ms to 10.9 ms ([#9057](https://github.com/holoviz/panel/pull/9057))
* Share the loading indicator CSS across all models on a Document instead of sending a copy per model, shrinking the initial document of a `Column` of 200 widgets from 126.7 KB to 74.5 KB (-41%) ([#9056](https://github.com/holoviz/panel/pull/9056))
* **Behaviour change:** Cut the per-event overhead in the server and notebook update paths and lower the default debounce of frontend changes from 50 ms to 20 ms; the browser to Python to browser round trip on the benchmark app dropped from a median of ~64 ms to ~34 ms. `pn.reactive.Syncable._debounce` can still be raised globally or per component ([#9066](https://github.com/holoviz/panel/pull/9066))
* Batch model updates scheduled from worker threads into one message and combine held events in linear time; a 1 ms periodic callback with `PANEL_NUM_THREADS=4` went from 299–390 to 603–682 ticks/s, and setting `TextInput.value` sends one message instead of two ([#9070](https://github.com/holoviz/panel/pull/9070))
* Process events that arrive while changes are still pending on a worker thread with the document lock, so a synchronous callback no longer blocks the event loop and its updates reach the browser while it runs ([#9075](https://github.com/holoviz/panel/pull/9075))
* Avoid redundant work on `Vega`, `HTML`, `Markdown` and `Plotly` pane updates: Vega data updates no longer re-embed the chart (mean latency 46.5 ms -> 22 ms), streaming 200 chunks containing math into `Markdown` went from 3665 ms to 465 ms of JS time, and a Plotly layout change made in the browser from 269 ms to 6 ms ([#9061](https://github.com/holoviz/panel/pull/9061))
* Update `Tabulator` incrementally in the browser on `stream`, `patch` and selection instead of rebuilding the table; a one-cell `patch` on 10k rows went from 15.3 ms to 0.4 ms of JS handler time ([#9065](https://github.com/holoviz/panel/pull/9065))
* Cut the Python-side cost of `Tabulator` updates on large tables; on 200k rows a remote pagination page change went from 13.9 ms to 1.2 ms and a one-cell `patch()` with a sorter active from 27.6 ms and a 6.3 MB message to 2.1 ms and a 1 KB message. Also fixes `patch()` with remote pagination ([#9071](https://github.com/holoviz/panel/pull/9071))
* Stop rebuilding every `Tabulator` column on each edit when column names are not strings (e.g. years after a pivot), which also closed the editor when tabbing to the next cell ([#9054](https://github.com/holoviz/panel/pull/9054))
* **Behaviour change:** Reduce `pn.cache` per-call overhead (a hit on `f(1)` went from 22.5 µs to 1.4 µs), give decorations with different settings separate caches and let an exact type in `hash_funcs` take precedence over the defaults. Hashes of flat containers change, so existing `to_disk=True` caches are recomputed once ([#9063](https://github.com/holoviz/panel/pull/9063))
* Release Documents cleaned up without a session (liveness checks, warm-up, the ASGI server) and cut references from models to their Document when it is destroyed, so they no longer stay alive forever ([#9059](https://github.com/holoviz/panel/pull/9059))

### 🔒 Security

* Reject `next_url` values such as `///evil.com` or ones containing control characters, which browsers resolve to another site, in the basic auth and OAuth login redirects ([#8938](https://github.com/holoviz/panel/pull/8938))

### 🐛 Bug Fixes

* Send updates made inside a long running synchronous callback to the browser while it runs instead of only once it returns, so e.g. a loading spinner toggled in the callback shows again, on Tornado as well as the ASGI servers ([#8937](https://github.com/holoviz/panel/pull/8937), [#9082](https://github.com/holoviz/panel/pull/9082))
* Only treat the document lock as held by the thread that acquired it, fixing `RuntimeError: _pending_writes should be non-None` and concurrent document writes in threaded apps (`--num-threads`), including on free-threaded Python 3.14, and only let the lock owner write updates directly from a worker thread ([#9008](https://github.com/holoviz/panel/pull/9008), [#9009](https://github.com/holoviz/panel/pull/9009), [#9024](https://github.com/holoviz/panel/pull/9024))
* Keep a script that ends right after `pn.serve(..., threaded=True)` serving, which since 1.10.0 answered every request with a 500 error ([#9073](https://github.com/holoviz/panel/pull/9073))
* Fix several timing issues: Plotly clicks and hovers right after render being dropped, quick `Tabs` switches leaving broken views, timers scheduled from worker threads firing late, a `Tabulator` scroll right after render being reset, `PeriodicCallback.start()` busy looping, and threaded servers leaking sockets on Windows ([#8869](https://github.com/holoviz/panel/pull/8869))
* Sync every property change of a message sent from the browser in notebooks, where only the first one reached Python, so e.g. `pn.state.browser_info` and `FileInput` `filename` and `mime_type` are populated ([#9045](https://github.com/holoviz/panel/pull/9045))
* Stop notebooks from echoing changes made in Python back to Python, which caused `BokehUserWarning: reference already known` warnings ([#9055](https://github.com/holoviz/panel/pull/9055))
* Stop sending a change made in the browser back to that browser when it arrives while the Document is held, e.g. by a callback running on a worker thread, which on high-latency deployments reset text inputs to stale text and lost the characters typed since ([#9101](https://github.com/holoviz/panel/pull/9101))
* Write changes from unlocked callbacks, such as an async task streaming into a chat message, after the changes of a callback holding the document lock when they refer to models that callback has not sent yet, instead of writing them first so the browser dropped them with `reference ... isn't known`; unrelated changes are still written immediately ([#9105](https://github.com/holoviz/panel/pull/9105), [#9107](https://github.com/holoviz/panel/pull/9107))
* Write the changes of a locked callback that are handed to Bokeh, e.g. when a `hold()` block exits while the socket is busy, as one message instead of one per change, so the browser no longer renders them in steps ([#9106](https://github.com/holoviz/panel/pull/9106))
* Keep every view of a notebook output responsive when the output is shown more than once, e.g. with JupyterLab's "Create New View for Cell Output" ([#9062](https://github.com/holoviz/panel/pull/9062))
* Fix `MultipleInstanceError` from `Kernel.instance()` (e.g. in ipyleaflet) after loading the `ipywidgets` extension, while still resolving the per-session kernel when serving ipywidgets from a notebook or the Jupyter preview, and render the first ipywidget of a served app reliably ([#8949](https://github.com/holoviz/panel/pull/8949), [#9025](https://github.com/holoviz/panel/pull/9025), [#9074](https://github.com/holoviz/panel/pull/9074))
* **Behaviour change:** Make OAuth and login redirects work behind a reverse proxy or with `--prefix` without `--oauth-redirect-uri`, honouring `X-Forwarded-Host` and `X-Forwarded-Prefix` with `--use-xheaders`. The default OAuth redirect URI now includes `--prefix` and follows those headers, so re-register it with your provider or pass `--oauth-redirect-uri` ([#9072](https://github.com/holoviz/panel/pull/9072), building on [#8211](https://github.com/holoviz/panel/pull/8211) by @TheoMathurin)
* **Behaviour change:** Leave hierarchical `Tabulator` group rows blank for index levels without an aggregator instead of summing every column (and concatenating strings). Pass `aggregators` explicitly, e.g. `aggregators={'grp': 'sum'}`, to keep the previous sums ([#9004](https://github.com/holoviz/panel/pull/9004), [#9011](https://github.com/holoviz/panel/pull/9011))
* Fix `Tabulator.stream` on a table whose index is a `DatetimeIndex` or another non-numeric index, preserving the streamed index labels so repeated streams and subsequent patches work ([#8858](https://github.com/holoviz/panel/pull/8858), [#9023](https://github.com/holoviz/panel/pull/9023))
* Convert `datetime`, `pd.Timestamp` and `np.datetime64` values in `Tabulator.patch`, which previously raised or wrote the wrong value ([#9000](https://github.com/holoviz/panel/pull/9000))
* Support clearing a cell in a nullable integer (`Int64`) `Tabulator` column, which now stores `<NA>` and keeps the dtype ([#8994](https://github.com/holoviz/panel/pull/8994))
* Re-fit `Tabulator` columns with a `fit_data` layout after a cell edit or a new `value`, so longer content no longer clips; columns the user resized keep their width ([#8968](https://github.com/holoviz/panel/pull/8968))
* Let a `Tabulator` date header filter with `func='like'` match the timestamp text instead of raising, with remote pagination and in `current_view` ([#8857](https://github.com/holoviz/panel/pull/8857))
* Apply `Tabulator.style` cell styles to the right column when `groups` are set ([#8966](https://github.com/holoviz/panel/pull/8966))
* **Behaviour change:** Ignore the `width` that a pandas `Styler` (e.g. `Styler.bar`) sets on `Tabulator` cells, which made the column wider than its header; use `Tabulator.widths` to size columns ([#8988](https://github.com/holoviz/panel/pull/8988))
* Stop highlighting rows on hover when `Tabulator` has `selectable=False` ([#8955](https://github.com/holoviz/panel/pull/8955))
* Support `Tabulator.jscallback(selection=...)` and raise a clear error when a `jscallback` targets a parameter that only exists in Python ([#8953](https://github.com/holoviz/panel/pull/8953))
* Stop a `Tabulator` in an inactive tab from keeping the browser's main thread busy ([#8936](https://github.com/holoviz/panel/pull/8936))
* Fix `Perspective.stream()` duplicating rows in the browser, make dict patches to `Perspective` update `.object`, and stop truncating edited Polars string values ([#8841](https://github.com/holoviz/panel/pull/8841))
* Keep datetime axes of a `Plotly` pane as dates after `update_traces` or `batch_update` ([#8952](https://github.com/holoviz/panel/pull/8952))
* Fix the serialization error that dropped `Plotly` updates made inside `fig.batch_update()` ([#8943](https://github.com/holoviz/panel/pull/8943))
* Include multicategory `x` values and heatmap and image `pointNumber`/`pointIndex` in `Plotly` click, hover and selection data ([#8954](https://github.com/holoviz/panel/pull/8954))
* Play animated `Plotly` figures by keeping their frames, also when the figure is given as a dict ([#9043](https://github.com/holoviz/panel/pull/9043))
* **Behaviour change:** Render `Matplotlib` PNGs at twice the `dpi` when `high_dpi=True` (the default), as before Panel 1.0, so they are sharp on high-DPI screens at the same displayed size; PNGs are about 2-3x larger and `high_dpi=False` restores the previous output ([#9047](https://github.com/holoviz/panel/pull/9047))
* Render Matplotlib plots in a `HoloViews` pane, e.g. of a `HoloMap` or `DynamicMap`, at the DPI of the HoloViews renderer, so they are no longer twice the size of the same plot rendered by HoloViews directly ([#9049](https://github.com/holoviz/panel/pull/9049))
* **Behaviour change:** Apply the `theme` of a `Bokeh` pane in served apps, notebooks and saved files by setting it on the document, as `HoloViews.theme` does, so it now applies to the whole document ([#8996](https://github.com/holoviz/panel/pull/8996))
* Style `Segment` glyphs, such as box plot whiskers, in the dark Bokeh themes so they are visible ([#8980](https://github.com/holoviz/panel/pull/8980))
* Load the full KaTeX stylesheet and bundle its fonts for the `LaTeX` pane, so constructs such as `\hline` render correctly ([#8965](https://github.com/holoviz/panel/pull/8965))
* Stop the `Markdown` pane from parsing `*` inside `$$...$$` math as emphasis, including while streaming ([#8970](https://github.com/holoviz/panel/pull/8970), [#9014](https://github.com/holoviz/panel/pull/9014))
* Stop an `HTML` or `Markdown` pane from throwing when its visibility changes before it is rendered, e.g. inside a collapsed `panel-material-ui` `Card` ([#9051](https://github.com/holoviz/panel/pull/9051))
* Support Altair's `vegafusion` data transformer in the `Vega` pane ([#8939](https://github.com/holoviz/panel/pull/8939))
* Render local PDF data in the `PDF` pane with `embed=False` in Chromium ([#8995](https://github.com/holoviz/panel/pull/8995))
* Keep the per-row structure of nested columns, such as `PathLayer` paths, in `DeckGL` data ([#8982](https://github.com/holoviz/panel/pull/8982))
* Generate Material UI widgets in `pn.ui.HoloViews`, and design-specific widgets in `pn.pane.HoloViews`, as intended ([#8976](https://github.com/holoviz/panel/pull/8976))
* Keep one `HoloViews` slider option per `HoloMap` key when formatted labels collide, so every frame can be selected ([#8984](https://github.com/holoviz/panel/pull/8984))
* Accept `pn.ui` layouts for `HoloViews.widget_layout` and `ChatReactionIcons.default_layout` ([#8932](https://github.com/holoviz/panel/pull/8932))
* Allow non-string values in `AutocompleteInput` with `restrict=False` ([#8909](https://github.com/holoviz/panel/pull/8909))
* Allow setting the `value` of `TextInput`, `TextAreaInput` and `PasswordInput` to `None` ([#8917](https://github.com/holoviz/panel/pull/8917))
* Show the default colour (`#000000`) when the `value` of a `ColorPicker` is set to `None`, instead of raising a validation error ([#9098](https://github.com/holoviz/panel/pull/9098))
* Allow `fixed_start` or `fixed_end` to be `None` on editable sliders, e.g. when generated by `pn.Param` for a parameter with one open bound, instead of raising a `TypeError` ([#9103](https://github.com/holoviz/panel/pull/9103))
* Select the right option in a `Select` with `groups` when the same label appears in several groups ([#8956](https://github.com/holoviz/panel/pull/8956))
* Select the right option when a `Select` synced to the URL has numeric-looking options such as `'02'` ([#8960](https://github.com/holoviz/panel/pull/8960))
* Fix validation of `DatetimeInput` when only `start` or `end` is set ([#8910](https://github.com/holoviz/panel/pull/8910))
* Show a rounded value (e.g. `0.1` instead of `0.10000000001`) in the `EditableFloatSlider` textbox when no `format` is given, and apply later `format` and `step` changes to it ([#8990](https://github.com/holoviz/panel/pull/8990))
* **Behaviour change:** Round `interact` slider defaults that fall between steps to the nearest step instead of flooring them, so `(0, 4, 0.5, 1.3)` now starts at `1.5` ([#8947](https://github.com/holoviz/panel/pull/8947), [#9013](https://github.com/holoviz/panel/pull/9013))
* Render a `None` value in `LinearGauge` like `nan` instead of raising a `TypeError` ([#9039](https://github.com/holoviz/panel/pull/9039))
* Size the animated stripes of an active `Progress` bar to its height ([#8981](https://github.com/holoviz/panel/pull/8981))
* Respect `max_width` and `max_height` when sizing the `Dial` ([#8958](https://github.com/holoviz/panel/pull/8958))
* Accept any `os.PathLike`, such as an `os.DirEntry` from `os.scandir`, as the `file` of a `FileDownload` ([#9090](https://github.com/holoviz/panel/pull/9090))
* Render bounded `param.DateRange` and `param.CalendarDateRange` parameters without a default in `Param` instead of failing to load the page ([#8859](https://github.com/holoviz/panel/pull/8859))
* Use an input widget for bounded `param.Number` and `param.Integer` parameters whose value is `None`, which previously failed to render ([#8983](https://github.com/holoviz/panel/pull/8983))
* Fix updating the `objects` of a `param.Selector` holding `Parameterized` instances in `Param` ([#8985](https://github.com/holoviz/panel/pull/8985))
* **Behaviour change:** `Widget.from_param` no longer wraps selectors of `Parameterized` objects in a `Row` with an expand toggle; pass `expand_button=True` to opt back in ([#8991](https://github.com/holoviz/panel/pull/8991))
* Hide a single unpacked `Param` widget when its parameter's `precedence` drops below the display threshold ([#8992](https://github.com/holoviz/panel/pull/8992))
* Update the tab title when a `Tabs` entry is renamed but keeps the same pane ([#8944](https://github.com/holoviz/panel/pull/8944))
* Support param references for `objects` in `Tabs`, `Accordion` and `FloatPanel` ([#8997](https://github.com/holoviz/panel/pull/8997))
* Retain parameters such as `closable` and `tabs_location` when cloning `Tabs` and `Accordion`, clamping `active` to the new objects ([#8999](https://github.com/holoviz/panel/pull/8999), [#9012](https://github.com/holoviz/panel/pull/9012))
* Fix `clone` for components whose read-only parameters were edited with `param.edit_constant` ([#8948](https://github.com/holoviz/panel/pull/8948))
* Size a `FloatPanel` with `contained=False` to its content, while respecting a height set through `config={'panelSize': ...}` ([#8987](https://github.com/holoviz/panel/pull/8987), [#9015](https://github.com/holoviz/panel/pull/9015))
* Make `FloatPanel` children with stretching sizing modes fill the panel height ([#9001](https://github.com/holoviz/panel/pull/9001))
* Let a `pn.ui.Modal` grow to fit wide content and apply an explicit `width` to the dialog ([#9030](https://github.com/holoviz/panel/pull/9030))
* Let `VSpacer` fill the sidebar height in the Fast, Vanilla, React and Bootstrap templates ([#8971](https://github.com/holoviz/panel/pull/8971))
* Paint plots placed in the modal of the Fast templates in Chromium ([#8972](https://github.com/holoviz/panel/pull/8972))
* Size `scale_both` and `scale_height` content, such as responsive HoloViews plots with an `aspect`, in the Fast template ([#8993](https://github.com/holoviz/panel/pull/8993))
* Use the accent colour for the active Bokeh toolbar tool in the Fast templates ([#9002](https://github.com/holoviz/panel/pull/9002))
* Show the slides when `SlidesTemplate` has `main_max_width` set ([#8978](https://github.com/holoviz/panel/pull/8978))
* Show the configured disconnect and ready notifications for templates built outside a session, e.g. before `template.show()` ([#8942](https://github.com/holoviz/panel/pull/8942))
* **Behaviour change:** Fix `ReactiveHTML` components with `'literal'` children failing to render the page, and render literal children as (sanitized) HTML markup rather than only their text content ([#8989](https://github.com/holoviz/panel/pull/8989))
* Detect `++` and `--` assignments to `data.*` in `ReactiveHTML` scripts and no longer mistake comparisons for assignments ([#8998](https://github.com/holoviz/panel/pull/8998))
* Report the correct `event.node` for `ReactiveHTML` callbacks shared between several nodes ([#8962](https://github.com/holoviz/panel/pull/8962))
* Stop a child from disappearing from `pn.ui` layouts when children are swapped in `ReactComponent` ([#8935](https://github.com/holoviz/panel/pull/8935))
* **Behaviour change:** Stop `model.useState` in `ReactComponent` from writing a stale value back over a newer model change, which could e.g. leave a widget stuck loading after `loading = True` followed by `loading = False`. `setValue` now writes to the model synchronously, so a value set through it reaches the server before a `send_msg` sent in the same handler ([#9100](https://github.com/holoviz/panel/pull/9100))
* Set up `jslink` and `jscallback` links on children added to a `JSComponent` or `ReactComponent` layout, e.g. with `pn.ui.Column.extend` ([#9028](https://github.com/holoviz/panel/pull/9028))
* Fix `JSComponent` and `ReactComponent` views that are re-rendered or removed before they mount, which could abort the layout of the whole page (e.g. with `Cannot read properties of undefined (reading 'top_panel')` for a Bokeh figure) or leave every component rendered afterwards blank ([#9081](https://github.com/holoviz/panel/pull/9081))
* Warn instead of raising when `.controls()` cannot link a parameter to a missing model property ([#8979](https://github.com/holoviz/panel/pull/8979))
* **Behaviour change:** Keep the loading indicator of an async `ParamFunction` or `ParamMethod` on until the function completes ([#8946](https://github.com/holoviz/panel/pull/8946))
* **Behaviour change:** Only inherit `Pipeline` stage values from stages on the current route, so values from abandoned branches no longer leak into a stage ([#8986](https://github.com/holoviz/panel/pull/8986))
* Serve applications whose name or route contains non-ASCII characters, and show their decoded names on the index page ([#8950](https://github.com/holoviz/panel/pull/8950), [#9017](https://github.com/holoviz/panel/pull/9017))
* Honor `pn.config.admin_endpoint` and `PANEL_ADMIN_ENDPOINT` ([#8945](https://github.com/holoviz/panel/pull/8945))
* Open a single browser tab when serving with `num_procs > 1` and `show=True` ([#8963](https://github.com/holoviz/panel/pull/8963))
* Mount WSGI apps such as Flask at their route and `prefix` so their routes resolve ([#8967](https://github.com/holoviz/panel/pull/8967))
* Change the ETag of a file served with `--static-dirs` when the file is rewritten, so browsers no longer keep a stale copy until a hard reload ([#8961](https://github.com/holoviz/panel/pull/8961))
* Read and write user files such as `--setup` scripts, auth templates, `panel convert` output and `panel compile` projects as UTF-8, fixing non-ASCII text on Windows ([#9036](https://github.com/holoviz/panel/pull/9036))
* **Behaviour change:** Only install Panel's SIGINT handler in `get_server` and `pn.serve` when `start=True`; applications that start the event loop themselves should handle SIGINT ([#9003](https://github.com/holoviz/panel/pull/9003))
* Reload the page when `pn.state.location.reload = True` is set while building the app, and no longer reload when it is set to `False` ([#8964](https://github.com/holoviz/panel/pull/8964))
* Give `pn.state.session_info` watchers distinct old and new values and make concurrent updates safe ([#8957](https://github.com/holoviz/panel/pull/8957), [#9016](https://github.com/holoviz/panel/pull/9016))
* Run `Terminal` subprocesses with `exec` so the server's exit handlers no longer run in the forked child ([#8940](https://github.com/holoviz/panel/pull/8940))
* Inline component stylesheets, e.g. for `Tabulator`, when saving with `resources='inline'` ([#8969](https://github.com/holoviz/panel/pull/8969))
* **Behaviour change:** Load lazily loaded component resources on hosts that rewrite or do not serve Panel's `static/extensions/` routes, such as Shiny. A library the host already loaded under a rewritten URL is recognised instead of fetched again, a failed resource request is retried once from the CDN instead of hanging, and ESM components always carry the es-module-shims URL. With `resources='server'`, a page now makes a request to the configured CDN when a `static/extensions/` request fails; a working server never does, and an air-gapped one sees that request fail as well ([#9020](https://github.com/holoviz/panel/pull/9020))
* Only merge embedded widgets that share a label when their type and options also match ([#8974](https://github.com/holoviz/panel/pull/8974))
* Fix `pn.cache` returning the result for a different float with the same hash, such as `-1.0` for `-2.0` ([#8922](https://github.com/holoviz/panel/pull/8922))
* Avoid a `RecursionError` when passing self-referential containers to a `pn.cache` function ([#8923](https://github.com/holoviz/panel/pull/8923))
* Fix typos in `panel compile` messages ([#8880](https://github.com/holoviz/panel/pull/8880))

### ⚙️ Compatibility

* **Behaviour change:** pandas is no longer a required dependency and moves to the `recommended` extra, as announced in the 1.9.0 release notes. `Tabulator`, the `DataFrame` widget, `Perspective`, `Vizzu` and `ChatMessage` work without it; the admin dashboard still requires pandas and raises a clear error without it ([#8841](https://github.com/holoviz/panel/pull/8841))
* Add compatibility with Bokeh 3.10.2, which clamps slider values to their range; editable sliders now widen their range in Python, and changing `fixed_start` or `fixed_end` clamps the value into the new bounds ([#8927](https://github.com/holoviz/panel/pull/8927))
* Stop passing the `HTTPServerRequest` arguments that Tornado 6.7 removed ([#9046](https://github.com/holoviz/panel/pull/9046))
* Bump `dompurify` to 3.4.17 ([#8908](https://github.com/holoviz/panel/pull/8908))

### ⚠️ Deprecations and Removals

* `TerminalSubprocess.run` keyword arguments other than `shell`, `cwd`, `env` and `executable` (e.g. `timeout` or `check`) are now ignored with a deprecation warning and will be removed in Panel 2.0 ([#8940](https://github.com/holoviz/panel/pull/8940))

### 📚 Documentation

* Add a Version 1.11 section to the upgrade guide, including the CDN fallback for server resources, and document the `compress` option of `pn.serve`, `PANEL_ADMIN_ENDPOINT` and the admin dashboard's pandas requirement, PNG export with Playwright, when MathJax is loaded, and that pandas is no longer installed with Panel ([#9078](https://github.com/holoviz/panel/pull/9078), [#9091](https://github.com/holoviz/panel/pull/9091))
* Cover the 1.11 changes in the reference gallery, including Polars and PyArrow data in the `DataFrame` widget, `Perspective` and `Vizzu`, `Tabulator` header filter placeholders, `Matplotlib.high_dpi` and automatic MathJax loading in `Markdown` ([#9079](https://github.com/holoviz/panel/pull/9079))
* Add a how-to guide for serving a REST API next to an app with a `--plugins` module, and record what the deprecated REST providers still do ([#9041](https://github.com/holoviz/panel/pull/9041))
* Add an "Other DataFrame libraries" section with a Polars example to the `Tabulator` reference ([#8841](https://github.com/holoviz/panel/pull/8841))
* Point the "Using Panel with an AI assistant" guide at the `llms.txt` and Markdown URLs that resolve, and remove the leftover reference notebook for the LangChain `PanelCallbackHandler` removed in 1.10, mapping `StreamlitCallbackHandler` to `ChatStep` in the Streamlit chat migration guide instead ([#9080](https://github.com/holoviz/panel/pull/9080))
* Document how to sync a list of `Parameterized` objects with the URL ([#8705](https://github.com/holoviz/panel/pull/8705))
* Document setting a favicon on standalone exports ([#9005](https://github.com/holoviz/panel/pull/9005))
* Add an introductory article and video to the Getting Started resources ([#8785](https://github.com/holoviz/panel/pull/8785))
* Correct the `Tabulator` reference, which stated that hierarchical index levels default to the `sum` aggregator ([#9011](https://github.com/holoviz/panel/pull/9011))
* Restore the Architecture and Styling sections in the Explanation navigation ([#8977](https://github.com/holoviz/panel/pull/8977))
* Remove nonexistent parameters from the `on_msg` and `show_server` docstrings ([#8926](https://github.com/holoviz/panel/pull/8926))
