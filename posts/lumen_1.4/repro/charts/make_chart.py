"""Run prompts through Lumen with Claude Code and save the chart Lumen makes.

usage: python make_chart.py NAME DATAFILE "prompt" ["follow-up" ...]
Writes charts/NAME.png (Lumen's own PNG export), NAME.yaml (the Vega-Lite spec),
NAME.sql and NAME.json (timing and model calls).
"""
import asyncio
import json
import sys
import time

from lumen.ai.editors import MultiChartEditor, SQLEditor, VegaLiteEditor
from lumen.ai.llm import ClaudeCode
from lumen.ai.ui import ExplorerUI

name, data, *prompts = sys.argv[1:]


async def main():
    llm = ClaudeCode()
    ui = ExplorerUI(data=data, llm=llm)
    await asyncio.sleep(0.5)
    start, error = time.time(), None
    with llm.trace() as events:
        for prompt in prompts:
            ui.interface.send(prompt, user="User", respond=False)
            try:
                await asyncio.wait_for(ui._chat_invoke(prompt, "User", ui.interface), timeout=900)
            except Exception as e:
                error = f"{type(e).__name__}: {str(e)[:200]}"
                break
    views = []
    for item in ui._explorations.items[1:]:
        exploration = item["view"]
        views += [v for v in (exploration.plan.views if exploration.plan else []) if isinstance(v, (VegaLiteEditor, SQLEditor))]
        for child in item.get("items", []):
            views += [v for v in child["view"].plan.views if isinstance(v, (VegaLiteEditor, SQLEditor))]
    charts = [v for v in views if isinstance(v, VegaLiteEditor) and not isinstance(v, MultiChartEditor)]
    sqls = [v for v in views if isinstance(v, SQLEditor)]
    record = {"name": name, "seconds": round(time.time() - start, 1), "error": error, "charts": len(charts),
              "model_calls": sum(1 for e in events if type(e).__name__ == "ModelCall"), "prompts": prompts}
    if charts:
        chart = charts[-1]
        open(f"charts/{name}.yaml", "w").write(chart.spec)
        view = chart.component
        params = view._get_params()["object"]
        record["debug"] = {
            "pipeline_table": view.pipeline.table,
            "spec_data_names": [l.get("data", {}).get("name") for l in (view.spec.get("layer") or [])] + [view.spec.get("data", {}).get("name")],
            "dataset_keys": list(params.get("datasets", {})),
            "dataset_rows": {k: len(v) for k, v in params.get("datasets", {}).items()},
            "columns": list(view.pipeline.data.columns),
        }
        out = chart.export("png")
        open(f"charts/{name}.png", "wb").write(out.getvalue())
    if sqls:
        open(f"charts/{name}.sql", "w").write(sqls[-1].spec)
    open(f"charts/{name}.json", "w").write(json.dumps(record, indent=1))
    print("DONE", json.dumps(record))


asyncio.run(main())
