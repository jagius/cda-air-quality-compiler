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

# order the csv files by province
province_order = ["bc", "ab", "sk", "mb", "on", "qc", "nb", "ns", "pe", "nl", "yt", "nt", "nu"]

# Loop through all province CSVs
for prov in province_order:
    csv_file = os.path.join("output", f"{prov}_air_quality.csv")
    df = pd.read_csv(csv_file)
    # Extract only the needed columns, rename for consistency
    temp = pd.DataFrame()
    temp['Location'] = df['Location']
    temp['Observed'] = df['Observed']
    # Merge with lookup on 'Location'
    merged = pd.merge(temp, lookup, left_on='Location', right_on='Index', how='left')
    # Select and rename columns as needed
    merged = merged.rename(columns={
        'lat': 'Latitude',
        'lon': 'Longitude',
        'Risk': 'Risk',
        'Label': 'Label'
    })
     # Add Risk column based on Observed
    merged['Risk'] = df['Observed'].map(risk_labels)
    # Add Label column as the string before the first comma in Location
    merged['Label'] = merged['Location'].str.split(',').str[0]
    compiled.append(merged[['Location', 'Observed', 'Latitude', 'Longitude', 'Risk', 'Label']])


# Concatenate all provinces
result = pd.concat(compiled, ignore_index=True)
# Remove rows where any column is blank (NaN)
result = result.dropna(how='all')

# Ensure the output directory exists
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

result.to_csv(os.path.join(output_dir, "compiled_air_quality.csv"), index=False)
print("Compiled CSV saved as compiled_air_quality.csv")