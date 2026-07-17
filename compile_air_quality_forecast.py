import pandas as pd
import glob
import os

# Read the lookup table
lookup = pd.read_csv("canada-air-quality-data_wildfires-xy_index.csv")

# Prepare a list to collect DataFrames
compiled = []

# update values for risk labels using a dictionary 
risk_labels = {
    "Low Risk": "Low (1-3)",
    "Moderate Risk": "Moderate (4-6)",
    "High Risk": "High (7-9)",
    "Very High Risk": "Very high (10+)"
}


def normalize_observed(value):
    if pd.isna(value):
        return pd.NA

    text = str(value).strip().lower()
    if not text:
        return pd.NA

    # Forecast pages may contain short or noisy tokens (e.g., "High", "Very", "calculated").
    if "very high" in text or text == "very":
        return "Very High Risk"
    if "moderate" in text:
        return "Moderate Risk"
    if "high" in text:
        return "High Risk"
    if "low" in text:
        return "Low Risk"

    return str(value).strip()

# order the csv files by province
province_order = ["bc", "ab", "sk", "mb", "on", "qc", "nb", "ns", "pe", "nl", "yt", "nt", "nu"]

# Loop through all province CSVs
for prov in province_order:
    csv_file = os.path.join("output", f"{prov}_air_quality_forecast.csv")  # use _forecast in forecast script

    if not os.path.exists(csv_file):
        print(f"Skipping {prov}: missing file {csv_file}")
        continue

    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Skipping {prov}: failed to read {csv_file} ({e})")
        continue

    # Validate required columns
    required = {"Location", "Observed"}
    if not required.issubset(df.columns):
        print(f"Skipping {prov}: missing required columns in {csv_file}")
        continue

    # Ensure optional forecast columns always exist to keep a stable output schema.
    forecast_columns = ["Day_Forecast", "Night_Forecast", "Next_Day_Forecast", "Next_Night_Forecast"]
    for col in forecast_columns:
        if col not in df.columns:
            df[col] = ""

    temp = pd.DataFrame()
    temp["Location"] = df["Location"]
    temp["Observed"] = df["Observed"]
    temp["Day_Forecast"] = df["Day_Forecast"]
    temp["Night_Forecast"] = df["Night_Forecast"]
    temp["Next_Day_Forecast"] = df["Next_Day_Forecast"]
    temp["Next_Night_Forecast"] = df["Next_Night_Forecast"]

    merged = pd.merge(temp, lookup, left_on="Location", right_on="Index", how="left")
    merged = merged.rename(columns={"lat": "Latitude", "lon": "Longitude"})

    merged["Observed"] = merged["Observed"].map(normalize_observed)
    merged["Risk"] = merged["Observed"].map(risk_labels).fillna("Unknown")
    merged["Label"] = merged["Location"].astype(str).str.split(",").str[0]

    compiled.append(merged[["Location", "Observed", "Day_Forecast", "Night_Forecast", "Next_Day_Forecast", "Next_Night_Forecast", "Latitude", "Longitude", "Risk", "Label"]])

if not compiled:
    raise RuntimeError("No province files were successfully compiled.")

# Concatenate all provinces
result = pd.concat(compiled, ignore_index=True)
# Remove rows where any column is blank (NaN)
result = result.dropna(how='all')

# Ensure the output directory exists
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

result.to_csv(os.path.join(output_dir, "compiled_air_quality_forecast.csv"), index=False)
print("Compiled CSV saved as compiled_air_quality_forecast.csv")