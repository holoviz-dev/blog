import asyncio

from lumen.ai.schemas import get_metaset
from lumen.sources.duckdb import DuckDBSource

url = "https://datasets.holoviz.org/penguins/v1/penguins.csv"
source = DuckDBSource(
    uri=":memory:",
    tables={"penguins": f"read_csv('{url}', nullstr='NA')"},
)
print(asyncio.run(get_metaset([source], ["penguins"])).compact_context())
