"""Download and trim the datasets the post's figures are made from, into charts/data/.

usage: python fetch_data.py
Idempotent: files that already exist are skipped.
"""
import io
import shutil
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "charts" / "data"
LUMEN_DATA = Path("~/repos/lumen/data").expanduser()

URLS = {
    "countries.geojson": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson",
    "gapminder.json": "https://cdn.jsdelivr.net/npm/vega-datasets@2.8.0/data/gapminder.json",
    "penguins.csv": "https://datasets.holoviz.org/penguins/v1/penguins.csv",
}
OWID = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
OWID_DC = "https://ourworldindata.org/grapher/data-centers-share-electricity-demand.csv?v=1&csvType=full&useColumnShortNames=true"
EPA ="https://aqs.epa.gov/aqsweb/airdata/annual_conc_by_monitor_2024.zip"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "holoviz-blog-repro"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    for name, url in URLS.items():
        if not (DATA / name).exists():
            (DATA / name).write_bytes(get(url))
            print("fetched", name)

    # UK electricity per capita by source (Our World in Data energy dataset)
    out = DATA / "uk_electricity.csv"
    if not out.exists():
        df = pd.read_csv(io.BytesIO(get(OWID)))
        cols = ["country", "year", "fossil_elec_per_capita", "nuclear_elec_per_capita", "renewables_elec_per_capita"]
        df = df.loc[df["country"] == "United Kingdom", cols].dropna(subset=cols[2:], how="all")
        df.to_csv(out, index=False)
        print("wrote", out.name, len(df))

    # PM2.5 annual means by monitor, 2024 (EPA AirData), one row per monitor
    out = DATA / "pm25_2024.csv"
    if not out.exists():
        with zipfile.ZipFile(io.BytesIO(get(EPA))) as z:
            df = pd.read_csv(z.open(z.namelist()[0]), low_memory=False)
        df = df[(df["Parameter Code"] == 88101) & (df["Sample Duration"] == "24 HOUR")]
        df = df[["State Name", "County Name", "City Name", "Site Num", "Latitude", "Longitude",
                 "Arithmetic Mean", "Observation Count", "Valid Day Count", "Required Day Count"]]
        df.to_csv(out, index=False)
        print("wrote", out.name, len(df))

    # Olympic medals (Lumen's sample data)
    for name in ["olympic_medals.csv"]:
        if not (DATA / name).exists():
            shutil.copy(LUMEN_DATA / name, DATA / name)
            print("copied", name)

    # Data-centre share of electricity demand (Our World in Data, from IEA and Ember)
    out = DATA / "data_centers_share.csv"
    if not out.exists():
        out.write_bytes(get(OWID_DC))
        print("fetched", out.name)


if __name__ == "__main__":
    main()
