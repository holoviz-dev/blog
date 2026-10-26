"""Draw the post's two composite images: the pipeline illustration and the hero collage.

usage:
    python illustrations.py pipeline   # images/pipeline.png, from charts/data/countries.geojson
    python illustrations.py collage    # images/collage_1.4.png, from the frames in images/
Both are an SVG/HTML page rendered by headless Chromium, so they rebuild the same every time.
"""
import asyncio
import base64
import math
import random
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from playwright.async_api import async_playwright

HERE = Path(__file__).parent
IMAGES = HERE.parent / "images"
DATA = HERE / "charts" / "data"

BLUES = ["#d6e6fa", "#b5d1f5", "#8fb8ee", "#6a9fe6", "#4a86da", "#2f6fcb", "#1f5bb5"]
ORANGE = "#f6b23c"
LINE = "#2563c4"


async def render(html, out, width, height, scale=2):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=scale)
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(500)
        await page.screenshot(path=out)
        await browser.close()
    print("wrote", out)


# ---------------------------------------------------------------- pipeline

def ring_path(coords, fx, fy):
    pts = [f"{fx(x):.1f},{fy(y):.1f}" for x, y in coords]
    return "M" + "L".join(pts) + "Z"


def world_paths(x0, y0, w, h):
    gdf = gpd.read_file(DATA / "countries.geojson")
    gdf = gdf[gdf["CONTINENT"] != "Antarctica"].to_crs("EPSG:8857")  # Equal Earth
    minx, miny, maxx, maxy = gdf.total_bounds
    s = min(w / (maxx - minx), h / (maxy - miny))
    ox, oy = x0 + (w - s * (maxx - minx)) / 2, y0 + (h - s * (maxy - miny)) / 2
    fx = lambda x: ox + (x - minx) * s
    fy = lambda y: oy + (maxy - y) * s
    pop = np.log10(gdf["POP_EST"].clip(lower=1e4))
    bins = np.linspace(pop.min(), pop.max(), len(BLUES) + 1)[1:-1]
    out = []
    for geom, p in zip(gdf.geometry, pop):
        polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
        d = "".join(ring_path(poly.exterior.coords, fx, fy) for poly in polys)
        out.append(f'<path d="{d}" fill="{BLUES[int(np.digitize(p, bins))]}" stroke="#fff" stroke-width="0.6"/>')
    return "\n".join(out)


def card(x, y, w, h, body, r=18):
    return (f'<g filter="url(#shadow)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="#fff" stroke="#dbe6f5"/></g>{body}')


def node(x, y, r=7):
    return (f'<circle cx="{x}" cy="{y}" r="{r + 7}" fill="{ORANGE}" opacity="0.25" filter="url(#glow)"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{ORANGE}" stroke="#fff" stroke-width="2.5"/>')


def wire(x1, y1, x2, y2, bend=0.5, width=3):
    cx = x1 + (x2 - x1) * bend
    return (f'<path d="M{x1},{y1} C{cx},{y1} {cx},{y2} {x2},{y2}" fill="none" stroke="{LINE}" '
            f'stroke-width="{width}" stroke-linecap="round" opacity="0.85"/>')


def db_icon(kind, x, y, s=84):
    cx, cy = x + s / 2, y + s / 2
    c = LINE
    if kind == "cylinder":
        g = "".join(f'<ellipse cx="{cx}" cy="{cy - 18 + i * 16}" rx="20" ry="7" fill="{c if i == 0 else "#fff"}" '
                    f'stroke="{c}" stroke-width="3"/>' for i in range(3))
        g = (f'<path d="M{cx - 20},{cy - 18} V{cy + 16} A20,7 0 0 0 {cx + 20},{cy + 16} V{cy - 18}" '
             f'fill="#e3ecfa" stroke="{c}" stroke-width="3"/>') + g
    elif kind == "cloud":
        g = (f'<path d="M{cx - 22},{cy + 12} a12,12 0 0 1 2,-24 a16,16 0 0 1 30,-4 a12,12 0 0 1 12,28 Z" '
             f'fill="#e3ecfa" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>')
    elif kind == "table":
        g = (f'<rect x="{cx - 22}" y="{cy - 18}" width="44" height="36" rx="4" fill="#fff" stroke="{c}" stroke-width="3"/>'
             f'<rect x="{cx - 22}" y="{cy - 18}" width="44" height="10" rx="3" fill="{c}"/>'
             + "".join(f'<line x1="{cx - 22}" x2="{cx + 22}" y1="{cy + 2 + i * 8}" y2="{cy + 2 + i * 8}" '
                       f'stroke="{c}" stroke-width="2"/>' for i in range(2))
             + f'<line x1="{cx - 4}" x2="{cx - 4}" y1="{cy - 8}" y2="{cy + 18}" stroke="{c}" stroke-width="2"/>')
    else:  # file
        g = (f'<path d="M{cx - 16},{cy - 22} h22 l12,12 v32 h-34 Z" fill="#fff" stroke="{c}" stroke-width="3" '
             f'stroke-linejoin="round"/><path d="M{cx + 6},{cy - 22} v12 h12" fill="none" stroke="{c}" stroke-width="3"/>'
             + "".join(f'<line x1="{cx - 9}" x2="{cx + 9}" y1="{cy + i * 7}" y2="{cy + i * 7}" stroke="{c}" '
                       f'stroke-width="2.5"/>' for i in range(3)))
    return card(x, y, s, s, g, r=14)


def pipeline_svg():
    random.seed(14)
    W, H = 1800, 900
    parts = []
    # chat bubble with a robot avatar
    bx, by, bw, bh = 120, 255, 520, 360
    parts.append(
        f'<g filter="url(#softglow)"><path d="M{bx + 40},{by} h{bw - 80} a40,40 0 0 1 40,40 v{bh - 80} '
        f'a40,40 0 0 1 -40,40 h{-(bw - 220)} l-120,70 l20,-70 h-60 a40,40 0 0 1 -40,-40 v{-(bh - 80)} '
        f'a40,40 0 0 1 40,-40 Z" fill="#fbfdff" stroke="{LINE}" stroke-width="4"/></g>')
    ax, ay = bx + 100, by + 95
    parts.append(
        f'<circle cx="{ax}" cy="{ay}" r="54" fill="#e6effb"/>'
        f'<line x1="{ax}" y1="{ay - 40}" x2="{ax}" y2="{ay - 26}" stroke="#16305c" stroke-width="4"/>'
        f'<circle cx="{ax}" cy="{ay - 42}" r="5" fill="#16305c"/>'
        f'<rect x="{ax - 32}" y="{ay - 26}" width="64" height="50" rx="16" fill="#16305c"/>'
        f'<rect x="{ax - 24}" y="{ay - 16}" width="48" height="28" rx="10" fill="#3d82e0"/>'
        f'<circle cx="{ax - 10}" cy="{ay - 3}" r="5" fill="#fff"/><circle cx="{ax + 10}" cy="{ay - 3}" r="5" fill="#fff"/>'
        f'<rect x="{ax - 40}" y="{ay - 8}" width="8" height="18" rx="3" fill="#16305c"/>'
        f'<rect x="{ax + 32}" y="{ay - 8}" width="8" height="18" rx="3" fill="#16305c"/>')
    for i, (w, o) in enumerate([(260, 0.35), (260, 0.3), (160, 0.45)]):
        parts.append(f'<rect x="{ax + 80}" y="{ay - 40 + i * 26}" width="{w}" height="12" rx="6" '
                     f'fill="#8fb3ea" opacity="{o + 0.2}"/>')
    parts.append(f'<rect x="{bx + 110}" y="{by + 175}" width="360" height="92" rx="40" fill="#cfe0f8"/>')
    for i, w in enumerate([300, 240, 150]):
        parts.append(f'<rect x="{bx + 145}" y="{by + 198 + i * 18}" width="{w}" height="8" rx="4" fill="{LINE}" opacity="{0.9 - i * 0.2}"/>')
    parts.append(f'<rect x="{bx + 50}" y="{by + 295}" width="84" height="40" rx="20" fill="#e6effb"/>'
                 + "".join(f'<circle cx="{bx + 72 + i * 20}" cy="{by + 315}" r="5" fill="#4a86da"/>' for i in range(3)))

    # cards
    mx, my, mw, mh = 820, 130, 620, 340
    parts.append(card(mx, my, mw, mh, world_paths(mx + 20, my + 20, mw - 40, mh - 40)))
    cx_, cy_, cw, ch = 850, 520, 440, 250
    bars = "".join(
        f'<rect x="{cx_ + 40 + i * 34}" y="{cy_ + ch - 40 - v}" width="24" height="{v}" rx="3" fill="#cfe0f8"/>'
        for i, v in enumerate([60, 80, 70, 100, 90, 120, 105, 140, 150, 170, 190]))
    pts = [(cx_ + 52 + i * 34, cy_ + ch - 60 - v) for i, v in enumerate([20, 50, 60, 40, 90, 65, 85, 110, 100, 130, 160])]
    line = (f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{LINE}" stroke-width="4" '
            f'stroke-linejoin="round"/>' + "".join(
                f'<circle cx="{x}" cy="{y}" r="7" fill="{ORANGE if i in (3, 10) else LINE}" stroke="#fff" stroke-width="2"/>'
                for i, (x, y) in enumerate(pts)))
    axis = f'<line x1="{cx_ + 30}" x2="{cx_ + cw - 30}" y1="{cy_ + ch - 38}" y2="{cy_ + ch - 38}" stroke="#9db7de" stroke-width="2"/>'
    parts.append(card(cx_, cy_, cw, ch, bars + axis + line))
    hx, hy, hw, hh = 1360, 485, 330, 290
    cells = []
    for r in range(7):
        for c in range(9):
            v = random.random()
            hot = (r, c) in {(2, 4), (3, 6), (4, 6), (4, 7), (5, 6)}
            col = "#f4d38c" if hot else BLUES[min(int(v * len(BLUES)), len(BLUES) - 1)]
            cells.append(f'<rect x="{hx + 22 + c * 32}" y="{hy + 22 + r * 35}" width="29" height="32" rx="3" fill="{col}"/>')
    parts.append(card(hx, hy, hw, hh, "".join(cells)))
    tiles = [(1560, 60 + i * 105) for i in range(4)]
    for kind, (x, y) in zip(["cylinder", "cloud", "table", "file"], tiles):
        parts.append(db_icon(kind, x, y))

    # wires: chat -> outputs, sources -> outputs
    port = [(bx + bw, by + 95 + i * 28) for i in range(4)]
    wires = [
        wire(*port[0], mx, my + 70), wire(*port[1], mx, my + 190),
        f'<path d="M{port[2][0]},{port[2][1]} C760,{port[2][1]} 1000,{cy_ - 90} 1000,{cy_}" fill="none" '
        f'stroke="{LINE}" stroke-width="3" opacity="0.85"/>', wire(*port[3], cx_, cy_ + 150, bend=0.35),
        wire(1290, 620, hx, 660, bend=0.5), wire(mx + mw, 280, 1520, 280, bend=0.6),
        wire(1520, 280, 1560, 102, bend=0.5, width=2.5), wire(1520, 280, 1560, 207, bend=0.5, width=2.5),
        wire(1520, 280, 1560, 312, bend=0.5, width=2.5), wire(1520, 280, 1560, 417, bend=0.5, width=2.5),
        wire(1520, 280, hx + 150, hy, bend=0.9),
    ]
    parts = parts[:1] + wires + parts[1:]
    nodes = [*port, (mx - 2, my + 70), (mx - 2, my + 190), (cx_ - 2, cy_ + 150), (1000, cy_ - 2),
             (hx - 2, 660), (1520, 280)]
    parts += [node(x, y) for x, y in nodes[4:]] + [node(x, y, 6) for x, y in port]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <radialGradient id="bg" cx="45%" cy="45%" r="75%"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#eef3fb"/></radialGradient>
  <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#2f5ea8" flood-opacity="0.10"/></filter>
  <filter id="softglow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="10" stdDeviation="18" flood-color="#3d82e0" flood-opacity="0.22"/></filter>
  <filter id="glow"><feGaussianBlur stdDeviation="4"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{"".join(parts)}
</svg>"""


# ---------------------------------------------------------------- collage

TILES = [  # (image, label, tile background); each frame is letterboxed, never cropped
    ("lumen_ui_map.png", "Maps", "#fff"),
    ("gapminder.png", "Charts from a sentence", "#fff"),
    ("medals.png", "Smarter Vega-Lite charts", "#fff"),
    ("electricity_stacked.png", "Follow-ups on the same chart", "#fff"),
    ("report_story.png", "Reports with a story", "#121212"),
    ("slope_ranking.png", "Labelled comparison", "#fff"),
]


def data_uri(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def collage_html():
    tiles = "".join(
        f'<figure><div class="frame" style="background:{bg}"><img src="{data_uri(IMAGES / f)}"></div>'
        f'<figcaption>{label}</figcaption></figure>'
        for f, label, bg in TILES)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html, body {{ margin: 0; }}
body {{ width: 1200px; height: 735px; overflow: hidden; color: #fff;
  font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
  background: radial-gradient(120% 140% at 0% 0%, #14306b 0%, #0f4b86 45%, #1a7a9c 100%); }}
header {{ padding: 26px 36px 14px; }}
h1 {{ margin: 0; font-size: 52px; font-weight: 800; letter-spacing: -1px; }}
p {{ margin: 8px 0 0; font-size: 19px; opacity: 0.85; }}
main {{ display: grid; grid-template-columns: repeat(3, 1fr); grid-template-rows: 1fr 1fr; gap: 14px 22px;
  padding: 0 30px; height: 590px; }}
figure {{ margin: 0; display: flex; flex-direction: column; min-height: 0; }}
.frame {{ flex: 1; min-height: 0; background: #fff; border-radius: 12px; overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, .28); display: flex; align-items: center; justify-content: center; }}
.frame img {{ width: 100%; height: 100%; object-fit: contain; padding: 6px; box-sizing: border-box; }}
figcaption {{ font-size: 16.5px; font-weight: 700; padding: 8px 4px 0; height: 24px; }}
</style></head><body>
<header><h1>Lumen 1.4</h1><p>Ask your data a question. Get maps, charts and reports.</p></header>
<main>{tiles}</main></body></html>"""


def main(which):
    if "pipeline" in which:
        asyncio.run(render(f"<html><body style='margin:0'>{pipeline_svg()}</body></html>",
                           IMAGES / "pipeline.png", 1800, 900, scale=1))
    if "collage" in which:
        asyncio.run(render(collage_html(), IMAGES / "collage_1.4.png", 1200, 735, scale=2))


if __name__ == "__main__":
    main(sys.argv[1:] or ["pipeline", "collage"])
