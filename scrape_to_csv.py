import pandas as pd
import ssl
import os
import time
import socket
from io import StringIO
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

provinces = ["bc", "ab", "sk", "mb", "on", "qc", "nb", "ns", "pe", "nl", "yt", "nt", "nu"]
# Specify the table index for each province/territory
table_indices = {
    "bc": 1, "ab": 1, "sk": 1, "mb": 1, "on": 1, "qc": 1, "nb": 1, "ns": 1, "pe": 1, "nl": 1, "yt": 1, "nt": 1, "nu": 1
}
base_url = "https://weather.gc.ca/airquality/pages/provincial_summary/{}_e.html"
ssl._create_default_https_context = ssl._create_unverified_context

REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3

# Ensure the output directory exists
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)


def fetch_tables(url: str):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                html = response.read().decode("utf-8", errors="replace")
            return pd.read_html(StringIO(html), flavor="lxml")
        except (HTTPError, URLError, socket.timeout, TimeoutError, ValueError) as err:
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"Failed to fetch/parse {url}: {err}") from err
            print(
                f"Attempt {attempt}/{MAX_RETRIES} failed for {url}: {err}. "
                f"Retrying in {RETRY_DELAY_SECONDS}s..."
            )
            time.sleep(RETRY_DELAY_SECONDS)

failed_provinces = []
for prov in provinces:
    url = base_url.format(prov)
    print(f"Processing {prov} from {url}", flush=True)
    try:
        tables = fetch_tables(url)
        table_index = table_indices.get(prov, 1)
        if table_index >= len(tables):
            raise IndexError(
                f"Table index {table_index} out of range for {prov}. "
                f"Found {len(tables)} tables."
            )
        df = tables[table_index]

        # Add 'Location' column (copy of first column)
        df['Location'] = df.iloc[:, 0].astype(str).apply(lambda x: f"{x}, {prov}, Canada")

        # Extract AQHI risk text from values like "2 Low Risk".
        df['Observed'] = df.iloc[:, 1].astype(str).str.split(' ', n=1).str[1]

        csv_filename = os.path.join(output_dir, f"{prov}_air_quality.csv")

        df.to_csv(csv_filename, index=False)
        print(f"Data scraped and saved to {csv_filename}", flush=True)
    except Exception as e:
        failed_provinces.append(prov)
        print(f"Error occurred for {prov}: {e}", flush=True)

if failed_provinces:
    raise RuntimeError(f"Scrape failed for provinces: {', '.join(failed_provinces)}")