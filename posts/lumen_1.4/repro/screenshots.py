"""Rebuild the Lumen 1.4 post's screenshots and chart exports.

usage:
    python fetch_data.py                    # once: datasets into charts/data/
    python screenshots.py                   # every shot
    python screenshots.py dark_map medals   # some shots

Each shot starts `charts/app_ui.py` (the data explorer, with the Claude Code
provider) on its own data, sends the prompts through the chat with Playwright,
waits for Lumen to finish, sets up the view and saves a PNG into ../images/.
Lumen's own chart exports land in charts/ui/ via the hook in app_ui.py.

A language model writes every chart, so each run gives different charts.
Needs `playwright install chromium`, and either the `claude` CLI signed in or
LUMEN_BLOG_PROVIDER=openai with OPENAI_API_KEY set (the env is passed to panel serve).
"""
import asyncio
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image
from playwright.async_api import Page, async_playwright

HERE = Path(__file__).parent
CHARTS = HERE / "charts"
IMAGES = HERE.parent / "images"
RAW = CHARTS / "raw"          # full-window captures, before cropping
UI_OUT = CHARTS / "ui"        # Lumen's PNG exports, written by app_ui.py
SCALE = 2                     # device pixel ratio for every capture
TIMEOUT = int(os.environ.get("SHOT_TIMEOUT_S", 15 * 60)) * 1000  # per prompt; LLMs can be slow

SHOTS = {
    "lumen_ui_map": dict(
        data=["data/countries.geojson"], size=(1400, 780),
        prompts=["Map each country's estimated population as a choropleth on a log colour scale "
                 "using the Equal Earth projection, with a legend."],
    ),
    "dark_map": dict(
        data=["data/pm25_2024.csv"], size=(1400, 900), theme="dark", crop="output", hover="Texas",
        prompts=["For each state in the air quality data, compute the average PM2.5 annual mean and "
                 "the number of unusable readings, where a monitor's valid days fall short of the "
                 "required days.",
                 "Create a choropleth of average PM2.5 by US state, with the state, average PM2.5 and "
                 "unusable readings in the tooltip."],
    ),
    "electricity_stacked": dict(
        data=["data/uk_electricity.csv"], size=(1280, 800), drawer=True,
        prompts=["Make a stacked area chart of the United Kingdom's Fossil fuels, Nuclear, and "
                 "Renewables per capita electricity from 2003 to the most recent year available."],
    ),
    "gapminder": dict(
        data=["data/gapminder.json"], size=(1400, 900), export=True,
        prompts=["For the ten most populous countries in 2005, draw a connected scatter plot of "
                 "fertility against life expectancy from 1955 to 2005, with bubbles sized by population "
                 "at each point and the country name at the 2005 end of each path."],
    ),
    "medals": dict(
        data=["data/olympic_medals.csv"], size=(1400, 900), export=True,
        prompts=["Which ten US athletes have won the most Olympic medals? Show them as a horizontal "
                 "stacked bar chart by medal type, coloured gold, silver and bronze, Michael Phelps on top.",
                 "Stack the segments in medal order, gold first from the axis, then silver, then bronze, "
                 "with the legend in the same order."],
    ),
    "slope_ranking": dict(
        data=["data/data_centers_share.csv"], size=(1400, 900), crop="output", pair=True,
        prompts=["Draw a slope chart of data centres' share of electricity demand from 2020 to 2025 for "
                 "the United States, China and the World, with the United States in red and the others "
                 "in muted colours, labelling each line.",
                 "Now rank the three by their 2025 share as a horizontal bar chart, highlighting the "
                 "United States and labelling each bar with its value."],
    ),
    "report_story": dict(
        data=["data/penguins.csv"], size=(1400, 760), theme="dark", report=True,
        prompts=["Give me an overview of the penguins dataset.",
                 "Show how many penguins there are of each species on each island as a stacked bar chart.",
                 "Plot flipper length against body mass, coloured by species."],
    ),
}


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def llm_env():
    """The environment for panel serve. Apps launched from the Dock or by Claude Desktop never
    read ~/.zshrc, so when OPENAI_API_KEY is missing, ask an interactive zsh for it."""
    env = dict(os.environ)
    if env.get("LUMEN_BLOG_PROVIDER", "openai") == "openai":
        env["LUMEN_BLOG_PROVIDER"] = "openai"
        if not env.get("OPENAI_API_KEY"):
            key = subprocess.run(["zsh", "-ic", "printenv OPENAI_API_KEY"], capture_output=True,
                                 text=True, timeout=30).stdout.strip()
            if not key:
                raise RuntimeError("OPENAI_API_KEY is not set in the environment or in ~/.zshrc")
            env["OPENAI_API_KEY"] = key
    return env


def serve(data):
    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "panel", "serve", "app_ui.py", "--port", str(port),
         "--allow-websocket-origin", f"localhost:{port}", "--args", *data],
        cwd=CHARTS, env=llm_env(), stdout=open(RAW / "serve.log", "a"), stderr=subprocess.STDOUT,
    )
    for _ in range(120):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=1).close()
            return proc, f"http://localhost:{port}/app_ui"
        except OSError:
            time.sleep(0.5)
    proc.kill()
    raise RuntimeError("panel serve did not start; see charts/raw/serve.log")


async def ask(page: Page, prompt: str, chart: bool = True):
    # A prompt can start a new exploration, which hides the last one's cards, so look
    # for a completion card we have not seen rather than for one more of them.
    done = page.get_by_text("Successfully completed")
    seen = set(await done.all_inner_texts())
    sent = page.get_by_text(prompt[:40])
    posted = await sent.count()
    box = page.get_by_placeholder("Ask anything...").last
    # Lumen ignores a message typed while it is still wrapping up the last answer,
    # so send until the prompt shows up in the chat.
    for _ in range(10):
        await box.fill(prompt)
        await box.press("Enter")
        await page.wait_for_timeout(3000)
        if await sent.count() > posted:
            break
    else:
        raise RuntimeError(f"prompt never posted: {prompt[:60]}")
    deadline = time.time() + TIMEOUT / 1000
    while not set(await done.all_inner_texts()) - seen:
        if time.time() > deadline:
            raise TimeoutError(f"no answer to: {prompt[:60]}")
        await page.wait_for_timeout(2000)
    await settle(page, chart=chart)


async def settle(page: Page, chart=True):
    await page.wait_for_load_state("networkidle")
    rendering = page.get_by_text("Rendering component")
    deadline = time.time() + 120
    while await rendering.count() and time.time() < deadline:
        await page.wait_for_timeout(1000)
    if chart:
        await page.locator(".vega-embed canvas, .vega-embed svg.marks").last.wait_for(timeout=120_000)
    await page.wait_for_timeout(2500)  # vega-embed animates in


async def set_drawer(page: Page, open_: bool):
    """Show or hide the Navigation drawer; the header button is labelled for its next action."""
    nav = page.get_by_text("Navigation", exact=True)
    is_open = await nav.count() > 0 and await nav.first.is_visible()
    if is_open != open_:
        # The header's menu button shares the label; the drawer's own chevron comes last.
        name = "Close drawer" if is_open else "Open drawer"
        await page.get_by_label(name).or_(page.get_by_title(name)).last.click()
        await page.wait_for_timeout(800)
    await refit(page)


async def refit(page: Page):
    """Vega sizes itself to its container once; a resize makes it fill the pane it ended up in."""
    size = page.viewport_size
    await page.set_viewport_size({"width": size["width"] - 1, "height": size["height"]})
    await page.wait_for_timeout(300)
    await page.set_viewport_size(size)
    await settle(page)
    await page.mouse.move(0, size["height"] - 1)  # park the pointer: no stray tooltips


async def output_box(page: Page):
    """Bounding box of the right-hand output pane (tabs, spec editor and chart)."""
    # Located from what is on screen, not the DOM: Panel nests the pane in shadow
    # roots, which innerText and parentElement walks do not cross.
    chart = await page.locator(".vega-embed").last.bounding_box()
    export = await page.get_by_text("Export Plot as").last.bounding_box()
    tabs_top = export["y"] - 75               # the step tabs sit one row above the toolbar
    left = min(chart["x"], export["x"]) - 16
    right = page.viewport_size["width"] - 10  # the pane runs to the window's right edge
    bottom = min(chart["y"] + chart["height"] + 16, page.viewport_size["height"])
    return {"x": left, "y": max(tabs_top, 0), "width": right - left, "height": bottom - max(tabs_top, 0)}


async def hover_until(page: Page, text: str):
    """Sweep the pointer over the chart until the Vega tooltip mentions `text`."""
    chart = await page.locator(".vega-embed").last.bounding_box()
    tooltip = page.locator("#vg-tooltip-element")
    for fy in [i / 24 for i in range(4, 22)]:
        for fx in [i / 32 for i in range(2, 30)]:
            await page.mouse.move(chart["x"] + fx * chart["width"], chart["y"] + fy * chart["height"])
            await page.wait_for_timeout(25)
            if await tooltip.count() and text in (await tooltip.inner_text()):
                return True
    return False


async def controls(page: Page):
    """Every labelled control, through shadow roots; printed when a report step is not found."""
    return await page.evaluate("""() => {
        const out = new Set();
        const walk = root => root.querySelectorAll('*').forEach(el => {
            const l = el.getAttribute('aria-label') || el.getAttribute('title');
            if (l) out.add(l);
            if (el.shadowRoot) walk(el.shadowRoot);
        });
        walk(document);
        return [...out];
    }""")


async def click_first(page: Page, names):
    for name in names:
        loc = page.get_by_role("button", name=name).or_(page.get_by_label(name)).or_(page.get_by_title(name))
        if await loc.count():
            await loc.first.click()
            return name
    print("  none of", names, "in", await controls(page), flush=True)
    return None


async def report(page: Page):
    await page.get_by_text("Report", exact=True).first.click()
    await settle(page, chart=False)
    await page.screenshot(path=RAW / "report_before.png")
    # Lumen's report toolbar is Material icon buttons whose descriptions are tooltips,
    # not labels, so click the icon ligatures: auto_stories = Annotate, get_app = Export.
    await page.get_by_text("auto_stories", exact=True).first.click()
    await page.get_by_role("button", name="Generate").click()
    # Lumen appends a "Story" tab and switches to it once the LLM has written the story
    await page.get_by_role("tab", name="Story").wait_for(timeout=TIMEOUT)
    await settle(page, chart=False)
    await page.wait_for_timeout(3000)
    await page.get_by_text("get_app", exact=True).first.click()
    await page.get_by_text("Word (.docx)").first.wait_for(timeout=10_000)
    # park the pointer on the export icon; a locator hover is refused while the menu's backdrop is up
    icon = await page.get_by_text("get_app", exact=True).first.bounding_box()
    await page.mouse.move(icon["x"] + icon["width"] / 2, icon["y"] + icon["height"] / 2)
    await page.wait_for_timeout(800)


async def shot(browser, name, spec):
    proc, url = serve(spec["data"])
    w, h = spec["size"]
    ctx = await browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=SCALE,
                                    color_scheme=spec.get("theme", "light"))
    page = await ctx.new_page()
    try:
        await page.goto(url + ("?theme=dark" if spec.get("theme") == "dark" else ""))
        await page.get_by_placeholder("Ask anything...").first.wait_for(timeout=120_000)
        await page.get_by_text("verifying").wait_for(state="hidden", timeout=120_000)
        if await page.get_by_text("Could not connect to the LLM").count():
            raise RuntimeError("Lumen could not reach its LLM; check `claude` login or OPENAI_API_KEY")
        pairs = []
        last = len(spec["prompts"]) - 1
        for i, prompt in enumerate(spec["prompts"]):
            # only some prompts draw: the final one, both halves of a pair, every report section
            await ask(page, prompt, chart=i == last or spec.get("pair") or (spec.get("report") and i > 0))
            if spec.get("pair"):
                pairs.append(RAW / f"{name}_{i}.png")
                await page.screenshot(path=pairs[-1], clip=await output_box(page))
        await set_drawer(page, spec.get("drawer", False))
        if spec.get("hover") and not await hover_until(page, spec["hover"]):
            print(f"  {name}: no tooltip for {spec['hover']}")
        if spec.get("report"):
            await report(page)
        raw = RAW / f"{name}.png"
        clip = await output_box(page) if spec.get("crop") == "output" else None
        await page.screenshot(path=raw, clip=clip)
        if spec.get("pair"):
            side_by_side(pairs, IMAGES / f"{name}.png")
        elif spec.get("export"):
            latest = max(UI_OUT.glob("*.png"), key=lambda p: p.stat().st_mtime)
            shutil.copy(latest, IMAGES / f"{name}.png")
        else:
            shutil.copy(raw, IMAGES / f"{name}.png")
        print(f"  {name}: saved")
    except Exception:
        await page.screenshot(path=RAW / f"{name}_failed.png")
        raise
    finally:
        await ctx.close()
        proc.terminate()


def side_by_side(paths, out, gap=40):
    ims = [Image.open(p).convert("RGB") for p in paths]
    h = max(i.height for i in ims)
    canvas = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) - 1), h), "white")
    x = 0
    for im in ims:
        canvas.paste(im, (x, 0))
        x += im.width + gap
    canvas.save(out)


async def main(names):
    RAW.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name in names:
            print(name)
            try:
                await shot(browser, name, SHOTS[name])
            except Exception as e:
                print(f"  {name}: FAILED {type(e).__name__}: {e}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:] or list(SHOTS)))
