import os
import pandas as pd

def check_excel_files():
    # Read stock codes from the text file
    with open('stock_codes.txt', 'r') as f:
        stock_codes = [line.strip() for line in f.readlines()]
    
    # Directory containing Excel files
    excel_dir = 'output'
    
    # Lists to store results
    valid_files = []  # Files with 108 rows
    invalid_files = []  # Files with different number of rows
    
    # Check each stock code
    for code in stock_codes:
        excel_path = os.path.join(excel_dir, f'{code}.xlsx')
        
        if not os.path.exists(excel_path):
            print(f"File not found: {excel_path}")
            continue
            
        try:
            # Read the Excel file
            df = pd.read_excel(excel_path)
            
            # Check number of rows
            if len(df) == 107:
                valid_files.append(code)
            else:
                invalid_files.append(code)
                print(f"{code}.xlsx has {len(df)} rows")
                
        except Exception as e:
            print(f"Error processing {code}.xlsx: {str(e)}")
    
    # Save results to text files
    with open('valid_files.txt', 'w') as f:
        f.write('\n'.join(valid_files))
    
    with open('invalid_files.txt', 'w') as f:
        f.write('\n'.join(invalid_files))
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total files checked: {len(stock_codes)}")
    print(f"Files with 107 rows: {len(valid_files)}")
    print(f"Files with different rows: {len(invalid_files)}")
    print("\nResults have been saved to valid_files.txt and invalid_files.txt")

if __name__ == "__main__":
    check_excel_files()
