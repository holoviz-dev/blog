import polars as pl

from lumen.pipeline import Pipeline
from lumen.sources.base import InMemorySource
from lumen.transforms import Aggregate, Filter

url = "https://datasets.holoviz.org/penguins/v1/penguins.csv"
penguins = pl.read_csv(url, null_values="NA")

pipeline = Pipeline(
    source=InMemorySource(tables={"penguins": penguins}),
    table="penguins",
    transforms=[
        Filter(conditions=[("island", "Biscoe")]),
        Aggregate(method="mean", by=["species"], columns=["body_mass_g"], with_index=False),
    ],
)
print(type(pipeline.data))
print(pipeline.data)
