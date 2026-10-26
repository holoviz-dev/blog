"""Lumen's data explorer, as `lumen-ai serve` runs it, that also saves every finished chart.

Each chart Lumen draws is written next to this folder's `ui/` output as a PNG
(Lumen's own export, 2x), plus its Vega-Lite spec, named by session and order.
"""
import os
import re
import sys
import time
from pathlib import Path

import panel as pn

from lumen.ai.editors import MultiChartEditor, VegaLiteEditor
from lumen.ai.llm import ClaudeCode, OpenAI
from lumen.ai.ui import ExplorerUI

OUT = Path(os.environ.get("LUMEN_BLOG_OUT", "ui"))
# screenshots.py passes the files for each shot as `panel serve app_ui.py --args FILE ...`
DATA = sys.argv[1:] or [
    "data/stocks.csv", "data/seattle-weather.csv", "data/gapminder.json",
    "data/countries.geojson", "data/airports.csv", "data/air.nc",
]


class BlogUI(ExplorerUI):

    async def _chat_invoke(self, *args, **kwargs):
        await super()._chat_invoke(*args, **kwargs)
        self._save_charts()

    def _editors(self):
        stack = [item for item in self._explorations.items[1:]]
        while stack:
            item = stack.pop(0)
            stack += item.get("items", [])
            plan = item["view"].plan
            for view in (plan.views if plan else []):
                if isinstance(view, VegaLiteEditor) and not isinstance(view, MultiChartEditor):
                    yield item["view"].title, view

    def _save_charts(self):
        OUT.mkdir(exist_ok=True)
        saved = getattr(self, "_saved", set())
        for title, editor in self._editors():
            if id(editor) in saved:
                continue
            saved.add(id(editor))
            stem = f"{self._session_tag}-{len(saved)}-{re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')}"
            (OUT / f"{stem}.yaml").write_text(editor.spec)
            (OUT / f"{stem}.png").write_bytes(editor.export("png").getvalue())
            print(f"SAVED {stem}", flush=True)
        self._saved = saved


tag = time.strftime("%H%M%S")
# LUMEN_BLOG_PROVIDER=openai uses OPENAI_API_KEY; the default is the Claude Code CLI
llm = OpenAI() if os.environ.get("LUMEN_BLOG_PROVIDER") == "openai" else ClaudeCode()
ui = BlogUI(data=DATA, llm=llm, title="Lumen AI - Data Explorer")
ui._session_tag = tag
ui.servable()
