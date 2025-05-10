import pandas as pd
import os
from typing import Tuple, Any

# Configuration for companies and their Excel files
COMPANY_CONFIGS = [
    {'excel_path': 'KCHOL.xlsx', 'ticker': 'KCHOL'},
    {'excel_path': 'SAHOL.xlsx', 'ticker': 'SAHOL'},
    {'excel_path': 'THYAO.xlsx', 'ticker': 'THYAO'},
    {'excel_path': 'TUPRS.xlsx', 'ticker': 'TUPRS'},
    {'excel_path': 'TCELL.xlsx', 'ticker': 'TCELL'},
    {'excel_path': 'TTKOM.xlsx', 'ticker': 'TTKOM'},
    {'excel_path': 'SISE.xlsx', 'ticker': 'SISE'},
    {'excel_path': 'TTRAK.xlsx', 'ticker': 'TTRAK'},
    {'excel_path': 'FROTO.xlsx', 'ticker': 'FROTO'},
    {'excel_path': 'TOASO.xlsx', 'ticker': 'TOASO'}
]

def update_excel_cell(
    excel_path: str,
    cell_position: Tuple[int, int],
    new_value: Any,
    sheet_name: str = 'Sheet1'
) -> None:
    """
    Update a specific cell in an Excel file with a new value.
    
    Args:
        excel_path (str): Path to the Excel file
        cell_position (Tuple[int, int]): Position of the cell as (row, column) indices (0-based)
        new_value (Any): New value to insert
        sheet_name (str): Name of the sheet to update (default: 'Sheet1')
    """
    try:
        # Read the Excel file
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        row_idx, col_idx = cell_position
        row_idx = row_idx - 2
        #col_idx = col_idx - 1
        # Check if the position is valid
        if row_idx >= len(df) or col_idx >= len(df.columns):
            raise ValueError(f"Cell position ({row_idx}, {col_idx}) is out of bounds")
        
        # Update the specific cell
        df.iloc[row_idx, col_idx] = new_value
        
        # Save the updated DataFrame back to Excel
        df.to_excel(excel_path, sheet_name=sheet_name, index=False)
        print(f"Successfully updated cell at position ({row_idx}, {col_idx}) in {excel_path}")
        
    except Exception as e:
        print(f"Error updating {excel_path}: {str(e)}")

def update_all_files_cell(
    cell_position: Tuple[int, int],
    new_value: Any,
    sheet_name: str = 'Sheet1'
) -> None:
    """
    Update a specific cell in all Excel files with the same value.
    
    Args:
        cell_position (Tuple[int, int]): Position of the cell as (row, column) indices (0-based)
        new_value (Any): New value to insert in all files
        sheet_name (str): Name of the sheet to update (default: 'Sheet1')
    """
    for config in COMPANY_CONFIGS:
        excel_path = config['excel_path']
        update_excel_cell(
            excel_path=excel_path,
            cell_position=cell_position,
            new_value=new_value,
            sheet_name=sheet_name
        )


def merge_duplicate_rows(file_name: str, sheet_name: str) -> pd.DataFrame:
    """
    1) Loads the given Excel sheet into a DataFrame.
    2) Finds any values in the first column that occur more than once.
    3) For each set of duplicates:
       - For each other column:
         • If exactly one of the rows has a non-null value, keep that.
         • If none have a value, leave it null.
         • If more than one non-null and they differ, print an error.
       - Writes the chosen values into the first occurrence.
       - Drops the remaining duplicate row(s).
    4) Resets the index and writes out to "<original>_merged.xlsx".
    5) Returns the merged DataFrame.
    """
    # --- Load ---
    df = pd.read_excel(file_name, sheet_name=sheet_name)
    key_col = df.columns[0]
    
    # Find duplicate keys
    counts = df[key_col].value_counts()
    duplicates = counts[counts > 1].index.tolist()
    
    for key in duplicates:
        idxs = df.index[df[key_col] == key].tolist()
        first_idx = idxs[0]
        
        # For each other column, resolve nulls/conflicts
        for col in df.columns[1:]:
            vals = df.loc[idxs, col]
            non_null = vals.dropna().unique()
            
            if len(non_null) == 1:
                # exactly one distinct non-null → use it
                df.at[first_idx, col] = non_null[0]
            elif len(non_null) == 0:
                # all null → leave as-is (NaN)
                df.at[first_idx, col] = pd.NA
            else:
                # conflict
                print(f"❌ Conflict for key '{key}' in column '{col}' at rows {idxs}: values = {non_null}")
                # choose to leave the first value or NaN; here we leave the first
                df.at[first_idx, col] = vals.iloc[0]
        
        # Drop all but the first duplicate
        df = df.drop(idxs[1:], axis=0)
    
    # Reset index, save, and return
    df = df.reset_index(drop=True)
    base, ext = os.path.splitext(file_name)
    out_name = f"{base}_merged{ext}"
    out_name = file_name
    df.to_excel(out_name, index=False, sheet_name=sheet_name)
    print(f"✅ Merged sheet saved to: {out_name}")
    return df

# Example usage:
if __name__ == "__main__":
    # Example: Update cell at position (0, 0) with the same value for all companies
    
    # update_all_files_cell((5, 0),  "Finansal Yatırımlar (Dönen)",                      "Bilanço")
    # update_all_files_cell((26, 0), "Finansal Yatırımlar (Duran)",                      "Bilanço")

    # update_all_files_cell((7, 0),  "Ticari Alacaklar (Dönen)",                         "Bilanço")
    # update_all_files_cell((28, 0), "Ticari Alacaklar (Duran)",                         "Bilanço")

    # update_all_files_cell((8, 0),  "Finans Sektörü Faaliyetlerinden Alacaklar (Dönen)",  "Bilanço")
    # update_all_files_cell((29, 0), "Finans Sektörü Faaliyetlerinden Alacaklar (Duran)",  "Bilanço")

    # update_all_files_cell((10, 0), "Diğer Alacaklar (Dönen)",                          "Bilanço")
    # update_all_files_cell((30, 0), "Diğer Alacaklar (Duran)",                          "Bilanço")

    # update_all_files_cell((11, 0), "Müşteri Sözleşmelerinden Doğan Varlıklar (Dönen)",  "Bilanço")
    # update_all_files_cell((31, 0), "Müşteri Sözleşmelerinden Doğan Varlıklar (Duran)",  "Bilanço")

    # update_all_files_cell((12, 0), "İmtiyaz Sözleşmelerine İlişkin Finansal Varlıklar (Dönen)", "Bilanço")
    # update_all_files_cell((32, 0), "İmtiyaz Sözleşmelerine İlişkin Finansal Varlıklar (Duran)", "Bilanço")

    # update_all_files_cell((13, 0), "Türev Araçlar (Dönen)",                             "Bilanço")
    # update_all_files_cell((33, 0), "Türev Araçlar (Duran)",                             "Bilanço")
    # update_all_files_cell((58, 0), "Türev Araçlar (Kısa Vadeli)",                       "Bilanço")
    # update_all_files_cell((77, 0), "Türev Araçlar (Uzun Vadeli)",                       "Bilanço")

    # update_all_files_cell((14, 0), "Stoklar (Dönen)",                                   "Bilanço")
    # update_all_files_cell((34, 0), "Stoklar (Duran)",                                   "Bilanço")

    # update_all_files_cell((16, 0), "Canlı Varlıklar (Dönen)",                          "Bilanço")
    # update_all_files_cell((36, 0), "Canlı Varlıklar (Duran)",                          "Bilanço")

    # update_all_files_cell((17, 0), "Peşin Ödenmiş Giderler (Dönen)",                   "Bilanço")
    # update_all_files_cell((42, 0), "Peşin Ödenmiş Giderler (Duran)",                   "Bilanço")

    # update_all_files_cell((20, 0), "Nakit Dışı Serbest Kullanılabilir Teminatlar (Dönen)", "Bilanço")
    # update_all_files_cell((45, 0), "Nakit Dışı Serbest Kullanılabilir Teminatlar (Duran)", "Bilanço")

    # update_all_files_cell((50, 0), "Finansal Borçlar (Kısa Vadeli)",                   "Bilanço")
    # update_all_files_cell((68, 0), "Finansal Borçlar (Uzun Vadeli)",                   "Bilanço")

    # update_all_files_cell((51, 0), "Diğer Finansal Yükümlülükler (Kısa Vadeli)",       "Bilanço")
    # update_all_files_cell((69, 0), "Diğer Finansal Yükümlülükler (Uzun Vadeli)",       "Bilanço")

    # update_all_files_cell((52, 0), "Ticari Borçlar (Kısa Vadeli)",                     "Bilanço")
    # update_all_files_cell((70, 0), "Ticari Borçlar (Uzun Vadeli)",                     "Bilanço")

    # update_all_files_cell((53, 0), "Finans Sektörü Faaliyetlerinden Borçlar (Kısa Vadeli)", "Bilanço")
    # update_all_files_cell((71, 0), "Finans Sektörü Faaliyetlerinden Borçlar (Uzun Vadeli)", "Bilanço")

    # update_all_files_cell((54, 0), "Çalışanlara Sağlanan Faydalar Kapsamında Borçlar (Kısa Vadeli)", "Bilanço")
    # update_all_files_cell((72, 0), "Çalışanlara Sağlanan Faydalar Kapsamında Borçlar (Uzun Vadeli)", "Bilanço")

    # update_all_files_cell((55, 0), "Diğer Borçlar (Kısa Vadeli)",                      "Bilanço")
    # update_all_files_cell((73, 0), "Diğer Borçlar (Uzun Vadeli)",                      "Bilanço")

    # update_all_files_cell((56, 0), "Müşteri Sözleşmelerinden Doğan Yükümlülükler (Kısa Vadeli)", "Bilanço")
    # update_all_files_cell((74, 0), "Müşteri Sözleşmelerinden Doğan Yükümlülükler (Uzun Vadeli)", "Bilanço")

    # update_all_files_cell((57, 0), "Özkaynak Yöntemiyle Değerlenen Yatırımlardan Yükümlülükler (Kısa Vadeli)", "Bilanço")
    # update_all_files_cell((76, 0), "Özkaynak Yöntemiyle Değerlenen Yatırımlardan Yükümlülükler (Uzun Vadeli)", "Bilanço")

    # update_all_files_cell((59, 0), "Devlet Teşvik ve Yardımları (Kısa Vadeli)",        "Bilanço")
    # update_all_files_cell((75, 0), "Devlet Teşvik ve Yardımları (Uzun Vadeli)",        "Bilanço")
    # update_all_files_cell((78, 0), "Devlet Teşvik ve Yardımları (Uzun Vadeli)",        "Bilanço")

    # update_all_files_cell((60, 0), "Ertelenmiş Gelirler (Kısa Vadeli)",                "Bilanço")
    # update_all_files_cell((79, 0), "Ertelenmiş Gelirler (Uzun Vadeli)",                "Bilanço")


    for config in COMPANY_CONFIGS:
        excel_path = config['excel_path']
        merged_df = merge_duplicate_rows(excel_path, "Bilanço")