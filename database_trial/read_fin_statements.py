import pandas as pd

# Path to the Excel file
excel_path = 'KCHOL.xlsx'

# 1. Load the workbook and list sheet names
xls = pd.ExcelFile(excel_path)
print("Available sheets:", xls.sheet_names)

# 2. Parse all sheets into a dictionary of DataFrames
sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}

# Example: Inspect the first few rows of a sheet
sheet_name = xls.sheet_names[0]  # change this to the sheet you want
df = sheets[sheet_name]
print(f"\nFirst rows of '{sheet_name}':")
print(df.head())

# 3. Assume your sheets have a column for the statement/item (e.g., 'Item') 
#    and other columns for each period (e.g., '2022', '2023Q1', etc.).
#    Inspect column names:
print("\nColumns in the sheet:", df.columns.tolist())

# 4. Function to get a specific financial value
def get_financial_value(sheet_name: str, item_name: str, period: str):
    """
    Returns the value for a given financial item and period from the specified sheet.
    """
    df = sheets[sheet_name]
    # Ensure the period column exists
    if period not in df.columns:
        raise ValueError(f"Period '{period}' not found in sheet '{sheet_name}'.")
    # Filter the row for the requested item
    row = df[df.iloc[:, 0] == item_name]
    if row.empty:
        raise ValueError(f"Item '{item_name}' not found in sheet '{sheet_name}'.")
    return row.iloc[0][period]

# 5. Example usage:
try:
    value = get_financial_value(sheet_name='Balance Sheet', 
                                item_name='Total Assets', 
                                period='2023')
    print(f"\nTotal Assets in 2023: {value}")
except Exception as e:
    print("Error:", e)

# 6. To get all periods for a given item:
def get_all_periods_for_item(sheet_name: str, item_name: str):
    df = sheets[sheet_name]
    row = df[df.iloc[:, 0] == item_name]
    if row.empty:
        raise ValueError(f"Item '{item_name}' not found in sheet '{sheet_name}'.")
    # Return a Series of period:value pairs
    return row.iloc[0, 1:]

# Example:
try:
    series = get_all_periods_for_item(sheet_name='Bilanço',
                                      item_name='    Toplam Kaynaklar')
    print(f"\nNet Income across periods:\n{series}")
except Exception as e:
    print("Error:", e)

