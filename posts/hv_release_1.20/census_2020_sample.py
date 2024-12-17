import dask.dataframe as dd

path = "~/Downloads/census2020.parq"
(x0, x1), (y0, y1) = (-8266484.09, -8204266.51), (4935561.21, 5000192.32)  # New York City

ddf = dd.read_parquet(path)

mask = (ddf.x.between(x0, x1)) & (ddf.y.between(y0, y1))

df = ddf[mask].compute().sample(n=100_000)
df.to_parquet("census_2020_sample.parq")
