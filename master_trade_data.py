import pandas as pd

# Load the Excel file
file_path = "DataWeb-Query-Export.xlsx"
xls = pd.ExcelFile(file_path)

# Display sheet names for inspection
sheet_names = xls.sheet_names
print(sheet_names)

# Define the target columns
target_columns = [
    "HTS", "description", "country", "year",
    "Customs Value", "First Unit", "Second Unit",
    "Landed Duty-Paid Value", "Dutiable Value",
    "Calculated Duties", "Import Charges", "CIF Import Value"
]

# Dictionary to map sheet names to corresponding column names
sheet_to_column = {
    "Customs Value": "Customs Value",
    "First Unit of Quantity": "First Unit",
    "Second Unit of Quantity": "Second Unit",
    "Landed Duty-Paid Value": "Landed Duty-Paid Value",
    "Dutiable Value": "Dutiable Value",
    "Calculated Duties": "Calculated Duties",
    "Import Charges": "Import Charges",
    "CIF Import Value": "CIF Import Value"
}

# Initialize an empty DataFrame to merge all data
master_df = pd.DataFrame()

# Process each relevant sheet and merge
for sheet, value_column in sheet_to_column.items():
    df = pd.read_excel(xls, sheet_name=sheet)

    # Normalize column names to handle inconsistencies
    df.columns = df.columns.str.strip().str.lower()
    
    # Rename known columns for consistency
    rename_dict = {
        'htsus number': 'HTS',
        'hts number': 'HTS',
        'product description': 'description',
        'country name': 'country',
        'year': 'year',
        'customs value': 'Customs Value',
        'first unit of quantity': 'First Unit',
        'second unit of quantity': 'Second Unit',
        'landed duty-paid value': 'Landed Duty-Paid Value',
        'dutiable value': 'Dutiable Value',
        'calculated duties': 'Calculated Duties',
        'import charges': 'Import Charges',
        'cif import value': 'CIF Import Value',
        value_column.lower(): value_column
    }

    df.rename(columns=rename_dict, inplace=True)

    # Keep only relevant columns
    keep_cols = ['HTS', 'description', 'country', 'year', value_column]
    df = df[[col for col in keep_cols if col in df.columns]]

    # Merge into master_df
    if master_df.empty:
        master_df = df
    else:
        master_df = pd.merge(master_df, df, on=['HTS', 'description', 'country', 'year'], how='outer')

# Replace NaNs with 0 for numerical columns
value_cols = [col for col in target_columns if col not in ['HTS', 'description', 'country', 'year']]
master_df[value_cols] = master_df[value_cols].fillna(0)

# Remove rows where all value columns are zero
# Ensure only numeric columns are used for summation
numeric_value_cols = master_df[value_cols].select_dtypes(include='number').columns
master_df = master_df.loc[~(master_df[numeric_value_cols].sum(axis=1) == 0)]


# Aggregate by HTS, description, country, year
master_df = master_df.groupby(['HTS', 'description', 'country', 'year'], as_index=False)[value_cols].sum()

master_df.head()
master_df.to_csv('Plot_Trade_Data.csv', index=False)


