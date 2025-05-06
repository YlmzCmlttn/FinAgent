# read_and_fill_facts.py

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables for DB connection
load_dotenv()
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'database_trial'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'host': os.getenv('DB_HOST', 'postgres'),
    'port': os.getenv('DB_PORT', '5432')
}

# Sheet and file configurations
SHEET_NAME = 'Bilanço'
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

# Mapping from Turkish account names to your account.code values
ACCOUNT_TRANSLATIONS = {
    'Toplam Varlıklar': 'TOTAL_ASSETS',
    'Toplam Dönen Varlıklar': 'TOTAL_CURRENT_ASSETS',
    'Toplam Duran Varlıklar': 'TOTAL_FIXED_ASSETS',
    'Toplam Kaynaklar': 'TOTAL_RESOURCES',
    'Toplam Yükümlülükler': 'TOTAL_LIABILITIES',
    'Toplam Uzun Vadeli Yükümlülükler': 'TOTAL_LONG_TERM_LIABILITIES',
    'Toplam Kısa Vadeli Yükümlülükler': 'TOTAL_SHORT_TERM_LIABILITIES',
    'Toplam Özkaynaklar': 'TOTAL_EQUITY'
}

def parse_period(col_name: str):
    """
    Parse a column header like '2024/12' into (year, quarter).
    Raises ValueError if format is unexpected.
    """
    parts = col_name.split('/')
    if len(parts) != 2:
        raise ValueError(f"Invalid period format: {col_name}")
    year, month = int(parts[0]), int(parts[1])
    quarter = (month - 1) // 3 + 1
    return year, quarter

def read_and_fill_facts():
    """
    Reads each company's Excel Bilanço sheet, translates account names,
    looks up company_id, account_id, and period_id, then bulk-inserts
    financial facts into the database.
    """
    # 1) Connect and build lookup maps
    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ticker, company_id FROM company;")
            company_map = dict(cur.fetchall())

            cur.execute("SELECT code, account_id FROM account;")
            account_map = dict(cur.fetchall())

            cur.execute("SELECT year, quarter, period_id FROM period;")
            period_map = {(y, q): pid for y, q, pid in cur.fetchall()}

        records = []

        # 2) Process each Excel file
        for cfg in COMPANY_CONFIGS:
            df = pd.read_excel(cfg['excel_path'], sheet_name=SHEET_NAME, header=0)

            # Rename the first column to 'account_name'
            first_col = df.columns[0]
            df.rename(columns={first_col: 'account_name'}, inplace=True)

            # Clean up and translate account names
            df['account_name'] = df['account_name'].astype(str).str.strip()
            df['account_code'] = df['account_name'].map(ACCOUNT_TRANSLATIONS)
            df.dropna(subset=['account_code'], inplace=True)

            company_id = company_map.get(cfg['ticker'])
            if not company_id:
                continue

            # 3) For each period column, gather facts
            for col in df.columns.drop(['account_name', 'account_code']):
                try:
                    year, quarter = parse_period(col)
                except ValueError:
                    continue

                period_id = period_map.get((year, quarter))
                if not period_id:
                    continue

                sub = df[['account_code', col]].dropna(subset=[col])
                for _, row in sub.iterrows():
                    acct_code = row['account_code']
                    account_id = account_map.get(acct_code)
                    if not account_id:
                        continue
                    value = row[col]
                    records.append((company_id, period_id, account_id, value))

        # 4) Bulk-insert all collected records
        if records:
            with conn.cursor() as cur:
                insert_sql = """
                    INSERT INTO financial_fact
                      (company_id, period_id, account_id, value)
                    VALUES %s
                """
                execute_values(cur, insert_sql, records)
            conn.commit()
            print(f"Inserted {len(records)} new financial facts.")
        else:
            print("No new financial facts to insert.")

