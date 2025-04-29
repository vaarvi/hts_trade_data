import requests
import pandas as pd
import os


api_token = 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyMDAxNDAwIiwianRpIjoiMmZjZmRiNDYtNTMyNC00MTZhLTlmMDUtMmFkMzcwN2RkNmY1IiwiaXNzIjoiZGF0YXdlYiIsImlhdCI6MTc0NDk5NzMwNywiZXhwIjoxNzQ2MjA2OTA3fQ.Or4JeGmabfgRBG7FTzBDM_EuopcHEazVTVcY-_irJ5WfafteR6oomSwggC6WSNjwZn_fXYi3f7IrhjrwBC6d9Q'

# HTS code to query
hts_code = '0101.21.0000'
# hts_codes = 721420000,73063050,73069010,730890,7308909590,731815,731816,73182100,7326908688,7610900080,7616107030,8302303060,84798995,8479899599,8479899899,8479909596,850421,850422,850423,8504314065,8504314065,850434,8535210000,8535210000,853529,8535400000,8535400000,8535904000,8536200020,8536200040,8537109170,853720,8538906000,854620,85011060,85013140,84122100,84834050,8501,83024960,84879000,84718010,85371090
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {api_token}"
}

# Input parameters
request_data = {
    "reporter": "USA",
    "partner": "All",  # All countries
    "type": "Annual",
    "frequency": "Annual",
    "classification": "HTS",
    "codes": [hts_code],
    "startYear": 2024,
    "endYear": 2024,
    "tradeFlow": "Import",
    "includeDescendants": False,  # Individual commodities
    "aggregateByProgram": "CSC",  # Import program aggregation
    "aggregateByProvisions": "RPCODE",
    "aggregateByDistrict": True
}

response = requests.post(
    "https://datawebws.usitc.gov/dataweb/api/v2/report2/runReport",
    headers=headers,
    json=request_data
)

if response.status_code == 200:
    data = response.json()
    rows = data['dto']['tables'][0]['row_groups'][0]['rowsNew']
    column_groups = data['dto']['tables'][0]['column_groups']

    # Extract all column labels
    columns = []
    for group in column_groups:
        for col in group['columns']:
            columns.append(col['label'])

    # Get values from each row
    processed_data = []
    for row in rows:
        values = [entry['value'] for entry in row['rowEntries']]
        processed_data.append(values)

    df = pd.DataFrame(processed_data, columns=columns)

    # Reorder to put 'Country' (partner) first, then sort by 'Customs Value'
    col_order = ['Partner Name'] + [col for col in df.columns if col != 'Partner Name']
    df = df[col_order]

    # Sort by 'Customs Value'
    customs_value_col = next((col for col in df.columns if 'Customs' in col and 'Value' in col), None)
    if customs_value_col:
        df[customs_value_col] = pd.to_numeric(df[customs_value_col].str.replace(",", ""), errors='coerce')
        df = df.sort_values(by=customs_value_col, ascending=False)

    # Output path
    output_dir = './data'
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{hts_code.replace('.', '')}_2024_import_data.csv")
    df.to_csv(file_path, index=False)

else:
    print(f"API Error: {response.status_code} - {response.text}")
