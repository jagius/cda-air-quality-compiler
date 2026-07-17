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


def extract_token(series, token_index):
    # Safely split scraped values that may be numbers, NaN, or empty strings.
    def _extract(value):
        if pd.isna(value):
            return ""
        tokens = str(value).split()
        if not tokens:
            return ""
        if token_index < len(tokens):
            return tokens[token_index]
        return tokens[-1]

    return series.map(_extract)

for prov in provinces:
    url = base_url.format(prov)
    try:
        tables = pd.read_html(url)
        table_index = table_indices.get(prov, 1)
        df = tables[table_index]

        # Add 'Location' column (copy of first column)
        df['Location'] = df.iloc[:, 0].astype(str).apply(lambda x: f"{x}, {prov}, Canada")

        # Add 'Observed' column (second token from second column when present)
        df['Observed'] = extract_token(df.iloc[:, 1], 1)
        # Add 'Day_Forecast' column (first token from third column)
        df['Day_Forecast'] = extract_token(df.iloc[:, 2], 0)
        # Add 'Night_Forecast' column (first token from fourth column)
        df['Night_Forecast'] = extract_token(df.iloc[:, 3], 0)
        # Add 'Next_Day_Forecast' column (first token from fifth column)
        df['Next_Day_Forecast'] = extract_token(df.iloc[:, 4], 0)
        # Add 'Next_Night_Forecast' column (first token from sixth column)
        df['Next_Night_Forecast'] = extract_token(df.iloc[:, 5], 0)

        csv_filename = os.path.join(output_dir, f"{prov}_air_quality_forecast.csv")

        df.to_csv(csv_filename, index=False)
        print(f"Data scraped and saved to {csv_filename}")
    except Exception as e:
        print(f"Error occurred for {prov}: {e}")