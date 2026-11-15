import pandas as pd

from lumen.ai.data_quality import lint_data

readings = pd.DataFrame({
    "station": ["north ", "south", "east", "west", "north ", "south"],
    "temp_c": [12.5, 13.0, -9999, 14.0, -9999, 15.0],
})
for finding in lint_data(readings):
    print("-", finding)
print("mean with the placeholders:", readings["temp_c"].mean())
