import pandas as pd
import ssl
import os

provinces = ["bc", "ab", "sk", "mb", "on", "qc", "nb", "ns", "pe", "nl", "yt", "nt", "nu"]
# Specify the table index for each province/territory
table_indices = {
    "bc": 1, "ab": 1, "sk": 1, "mb": 1, "on": 1, "qc": 1, "nb": 1, "ns": 1, "pe": 1, "nl": 1, "yt": 1, "nt": 1, "nu": 1
}
base_url = "https://weather.gc.ca/airquality/pages/provincial_summary/{}_e.html"
ssl._create_default_https_context = ssl._create_unverified_context

# Ensure the output directory exists
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

for prov in provinces:
    url = base_url.format(prov)
    try:
        tables = pd.read_html(url)
        table_index = table_indices.get(prov, 1)
        df = tables[table_index]

        # Add 'Location' column (copy of first column)
        df['Location'] = df.iloc[:, 0].astype(str).apply(lambda x: f"{x}, {prov}, Canada")

        # Add 'Observed' column (first word from second column)
        df['Observed'] = df.iloc[:, 1].astype(str).str.split(' ', n=1).str[1]

        csv_filename = os.path.join(output_dir, f"{prov}_air_quality.csv")

        df.to_csv(csv_filename, index=False)
        print(f"Data scraped and saved to {csv_filename}")
    except Exception as e:
        print(f"Error occurred for {prov}: {e}")