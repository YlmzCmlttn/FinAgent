import pandas as pd

def read_valid_tickers(file_path):
    """Read valid tickers from the text file."""
    with open(file_path, 'r') as file:
        valid_tickers = [line.strip() for line in file.readlines()]
    return set(valid_tickers)

def filter_companies():
    # Read valid tickers
    valid_tickers = read_valid_tickers('valid_files.txt')
    
    # Read companies CSV
    companies_df = pd.read_csv('companies.csv')
    
    # Create masks for valid and invalid companies
    valid_mask = companies_df['ticker'].isin(valid_tickers)
    
    # Split into valid and invalid companies
    valid_companies = companies_df[valid_mask]
    invalid_companies = companies_df[~valid_mask]
    
    # Save to separate CSV files
    valid_companies.to_csv('valid_companies.csv', index=False)
    invalid_companies.to_csv('invalid_companies.csv', index=False)
    
    # Print summary
    print(f"Total companies: {len(companies_df)}")
    print(f"Valid companies: {len(valid_companies)}")
    print(f"Invalid companies: {len(invalid_companies)}")

if __name__ == "__main__":
    filter_companies()
