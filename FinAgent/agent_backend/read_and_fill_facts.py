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

    # ACCOUNT_TRANSLATIONS entries
    'Nakit ve Nakit Benzerleri':                                'CASH_AND_CASH_EQUIVALENTS',
    'Gayrimenkul Projeleri Kapsamında Açılan Nakit Hesapları':  'CASH_ACCOUNTS_REAL_ESTATE_PROJECTS',
    'Finansal Yatırımlar (Dönen)':                              'FINANCIAL_INVESTMENTS_CURRENT',
    'Teminata Verilen Finansal Varlıklar':                     'CURRENT_PLEDGED_FINANCIAL_ASSETS',
    'Ticari Alacaklar (Dönen)':                                 'CURRENT_TRADE_RECEIVABLES',
    'Finans Sektörü Faaliyetlerinden Alacaklar (Dönen)':       'CURRENT_FINANCIAL_SECTOR_RECEIVABLES',
    'Türkiye Cumhuriyet Merkez Bankası Hesabı':                 'CENTRAL_BANK_OF_TURKEY_ACCOUNT',
    'Diğer Alacaklar (Dönen)':                                  'CURRENT_OTHER_RECEIVABLES',
    'Müşteri Sözleşmelerinden Doğan Varlıklar (Dönen)':        'CURRENT_ASSETS_FROM_CUSTOMER_CONTRACTS',
    'İmtiyaz Sözleşmelerine İlişkin Finansal Varlıklar (Dönen)': 'CURRENT_FINANCIAL_ASSETS_FROM_CONCESSION_CONTRACTS',
    'Türev Araçlar (Dönen)':                                    'CURRENT_DERIVATIVE_INSTRUMENTS',
    'Stoklar (Dönen)':                                          'CURRENT_INVENTORIES',
    'Proje Halindeki Stoklar':                                  'CURRENT_INVENTORIES_IN_PROGRESS',
    'Canlı Varlıklar (Dönen)':                                  'CURRENT_BIOLOGICAL_ASSETS',
    'Peşin Ödenmiş Giderler (Dönen)':                           'CURRENT_PREPAID_EXPENSES',
    'Ertelenmiş Sigortacılık Üretim Giderleri':                 'CURRENT_DEFERRED_INSURANCE_PRODUCTION_COSTS',
    'Cari Dönem Vergisiyle İlgili Varlıklar':                   'CURRENT_TAX_ASSETS',
    'Nakit Dışı Serbest Kullanılabilir Teminatlar (Dönen)':     'CURRENT_NON_CASH_FREELY_USABLE_COLLATERALS',
    'Diğer Dönen Varlıklar':                                    'OTHER_CURRENT_ASSETS',
    'Satış Amacıyla Elde Tutulan Duran Varlıklar':              'CURRENT_ASSETS_HELD_FOR_SALE',
    'Ortaklara Dağıtılmak Üzere Elde Tutulan Duran Varlıklar': 'CURRENT_ASSETS_HELD_FOR_DISTRIBUTION_TO_OWNERS',

    'Toplam Dönen Varlıklar': 'TOTAL_CURRENT_ASSETS',

    'Finansal Yatırımlar (Duran)':                             'FINANCIAL_INVESTMENTS_FIXED',
    'İştirakler, İş Ortaklıkları ve Bağlı Ortaklıklardaki Yatırımlar': 'FIXED_INVESTMENTS_IN_ASSOCIATES_JOINT_VENTURES_AND_SUBSIDIARIES',
    'Ticari Alacaklar (Duran)':                                'FIXED_TRADE_RECEIVABLES',
    'Finans Sektörü Faaliyetlerinden Alacaklar (Duran)':       'FIXED_FINANCIAL_SECTOR_RECEIVABLES',
    'Diğer Alacaklar (Duran)':                                 'FIXED_OTHER_RECEIVABLES',
    'Müşteri Sözleşmelerinden Doğan Varlıklar (Duran)':        'FIXED_ASSETS_FROM_CUSTOMER_CONTRACTS',
    'İmtiyaz Sözleşmelerine İlişkin Finansal Varlıklar (Duran)': 'FIXED_FINANCIAL_ASSETS_FROM_CONCESSION_CONTRACTS',
    'Türev Araçlar (Duran)':                                   'FIXED_DERIVATIVE_INSTRUMENTS',
    'Stoklar (Duran)':                                         'FIXED_INVENTORIES',
    'Özkaynak Yöntemiyle Değerlenen Yatırımlar':                'FIXED_EQUITY_METHOD_INVESTMENTS',
    'Canlı Varlıklar (Duran)':                                 'FIXED_BIOLOGICAL_ASSETS',
    'Yatırım Amaçlı Gayrimenkuller':                           'FIXED_INVESTMENT_PROPERTIES',
    'Proje Halindeki Yatırım Amaçlı Gayrimenkuller':           'FIXED_INVESTMENT_PROPERTIES_IN_PROGRESS',
    'Maddi Duran Varlıklar':                                   'FIXED_TANGIBLE_ASSETS',
    'Kullanım Hakkı Varlıkları':                               'FIXED_RIGHT_OF_USE_ASSETS',
    'Maddi Olmayan Duran Varlıklar':                           'FIXED_INTANGIBLE_ASSETS',
    'Peşin Ödenmiş Giderler (Duran)':                          'FIXED_PREPAID_EXPENSES',
    'Ertelenmiş Vergi Varlığı':                                'FIXED_DEFERRED_TAX_ASSETS',
    'Cari Dönem Vergisiyle İlgili Duran Varlıklar':            'FIXED_CURRENT_PERIOD_TAX_ASSETS',
    'Nakit Dışı Serbest Kullanılabilir Teminatlar (Duran)':    'FIXED_NON_CASH_FREELY_USABLE_COLLATERALS',
    'Diğer Duran Varlıklar':                                   'OTHER_FIXED_ASSETS',    

    'Toplam Duran Varlıklar': 'TOTAL_FIXED_ASSETS',

    'Toplam Varlıklar': 'TOTAL_ASSETS',

    'Finansal Borçlar (Kısa Vadeli)':                                     'SHORT_TERM_FINANCIAL_BORROWINGS',
    'Diğer Finansal Yükümlülükler (Kısa Vadeli)':                         'SHORT_TERM_OTHER_FINANCIAL_LIABILITIES',
    'Ticari Borçlar (Kısa Vadeli)':                                       'SHORT_TERM_TRADE_PAYABLES',
    'Finans Sektörü Faaliyetlerinden Borçlar (Kısa Vadeli)':               'SHORT_TERM_FINANCIAL_SECTOR_LIABILITIES',
    'Çalışanlara Sağlanan Faydalar Kapsamında Borçlar (Kısa Vadeli)':     'SHORT_TERM_EMPLOYEE_BENEFITS_LIABILITIES',
    'Diğer Borçlar (Kısa Vadeli)':                                        'SHORT_TERM_OTHER_BORROWINGS',
    'Müşteri Sözleşmelerinden Doğan Yükümlülükler (Kısa Vadeli)':          'SHORT_TERM_LIABILITIES_FROM_CUSTOMER_CONTRACTS',
    'Özkaynak Yöntemiyle Değerlenen Yatırımlardan Yükümlülükler (Kısa Vadeli)': 'SHORT_TERM_LIABILITIES_FROM_EQUITY_METHOD_INVESTMENTS',
    'Türev Araçlar (Kısa Vadeli)':                                       'SHORT_TERM_DERIVATIVE_LIABILITIES',
    'Devlet Teşvik ve Yardımları (Kısa Vadeli)':                          'SHORT_TERM_GOVERNMENT_GRANTS_AND_AIDS',
    'Ertelenmiş Gelirler (Kısa Vadeli)':                                  'SHORT_TERM_DEFERRED_INCOME',
    'Dönem Karı Vergi Yükümlülüğü':                                       'SHORT_TERM_INCOME_TAX_LIABILITIES',
    'Kısa Vadeli Karşılıklar':                                            'SHORT_TERM_PROVISIONS',
    'Diğer Kısa Vadeli Yükümlülükler':                                    'OTHER_SHORT_TERM_LIABILITIES',
    'Satış Amaçlı Sınıflandırılan Varlık Gruplarına İlişkin Yükümlülükler': 'SHORT_TERM_LIABILITIES_RELATING_TO_ASSETS_CLASSIFIED_AS_HELD_FOR_SALE',
    'Ortaklara Dağıtılmak Üzere Elde Tutulan Varlık Gruplarına İlişkin Yükümlülükler': 'SHORT_TERM_LIABILITIES_RELATING_TO_ASSETS_HELD_FOR_DISTRIBUTION_TO_OWNERS',
    
    'Toplam Kısa Vadeli Yükümlülükler': 'TOTAL_SHORT_TERM_LIABILITIES',

    # ACCOUNT_TRANSLATIONS entries
    'Finansal Borçlar (Uzun Vadeli)':                                 'LONG_TERM_FINANCIAL_BORROWINGS',
    'Diğer Finansal Yükümlülükler (Uzun Vadeli)':                     'LONG_TERM_OTHER_FINANCIAL_LIABILITIES',
    'Ticari Borçlar (Uzun Vadeli)':                                   'LONG_TERM_TRADE_PAYABLES',
    'Finans Sektörü Faaliyetlerinden Borçlar (Uzun Vadeli)':           'LONG_TERM_FINANCIAL_SECTOR_LIABILITIES',
    'Çalışanlara Sağlanan Faydalar Kapsamında Borçlar (Uzun Vadeli)': 'LONG_TERM_EMPLOYEE_BENEFITS_LIABILITIES',
    'Diğer Borçlar (Uzun Vadeli)':                                    'LONG_TERM_OTHER_BORROWINGS',
    'Müşteri Sözleşmelerinden Doğan Yükümlülükler (Uzun Vadeli)':      'LONG_TERM_LIABILITIES_FROM_CUSTOMER_CONTRACTS',
    'Devlet Teşvik ve Yardımları (Uzun Vadeli)':                      'LONG_TERM_GOVERNMENT_GRANTS_AND_AIDS',
    'Özkaynak Yöntemiyle Değerlenen Yatırımlardan Yükümlülükler (Uzun Vadeli)': 'LONG_TERM_LIABILITIES_FROM_EQUITY_METHOD_INVESTMENTS',
    'Türev Araçlar (Uzun Vadeli)':                                    'LONG_TERM_DERIVATIVE_LIABILITIES',
    'Ertelenmiş Gelirler (Uzun Vadeli)':                              'LONG_TERM_DEFERRED_INCOME',
    'Uzun vadeli Karşılıklar':                                        'LONG_TERM_PROVISIONS',
    'Cari Dönem Vergisiyle İlgili Borçlar':                           'LONG_TERM_CURRENT_PERIOD_TAX_LIABILITIES',
    'Ertelenmiş Vergi Yükümlülüğü':                                   'LONG_TERM_DEFERRED_TAX_LIABILITIES',
    'Diğer Uzun Vadeli Yükümlülükler':                                'OTHER_LONG_TERM_LIABILITIES',

    'Toplam Uzun Vadeli Yükümlülükler': 'TOTAL_LONG_TERM_LIABILITIES',

    'Toplam Yükümlülükler': 'TOTAL_LIABILITIES',

    'Ana Ortaklığa Ait Özkaynaklar':                                             'EQUITY_ATTRIBUTABLE_TO_OWNERS_OF_PARENT',
    'Ödenmiş Sermaye':                                                          'PAID_IN_CAPITAL',
    'Sermaye Düzeltme Farkları':                                                'CAPITAL_ADJUSTMENT_DIFFERENCES',
    'Birleşme Denkleştirme Hesabı':                                              'MERGER_EQUALISATION_ACCOUNT',
    'Pay Sahiplerinin İlave Sermaye Katkıları':                                  'ADDITIONAL_PAID_IN_CAPITAL',
    'Sermaye Avansı':                                                            'CAPITAL_ADVANCE',
    'Geri Alınmış Paylar (-)':                                                   'TREASURY_SHARES',
    'Karşılıklı İştirak Sermaye Düzeltmesi (-)':                                 'RECIPROCAL_INVESTMENT_CAPITAL_ADJUSTMENT',
    'Paylara İlişkin Primler (İskontolar)':                                      'SHARE_PREMIUMS',
    'Ortak Kontrole Tabi Teşebbüs veya İşletmeleri İçeren Birleşmelerin Etkisi': 'EFFECT_OF_BUSINESS_COMBINATIONS_UNDER_COMMON_CONTROL',
    'Pay Bazlı Ödemeler (-)':                                                    'SHARE_BASED_PAYMENTS',
    'Kar veya Zararda Yeniden Sınıflandırılmayacak Birikmiş Diğer Kapsamlı Gelirler (Giderler)': 'ACCUMULATED_OTHER_COMPREHENSIVE_INCOME_NOT_RECLASSIFIED',
    'Kar veya Zararda Yeniden Sınıflandırılacak Birikmiş Diğer Kapsamlı Gelirler (Giderler)':   'ACCUMULATED_OTHER_COMPREHENSIVE_INCOME_RECLASSIFIED',
    'Kardan Ayrılan Kısıtlanmış Yedekler':                                       'RESTRICTED_RESERVES_APPROPRIATED_FROM_PROFIT',
    'Diğer Özkaynak Payları':                                                    'OTHER_EQUITY_INTERESTS',
    'Diğer Yedekler':                                                            'OTHER_RESERVES',
    'Ödenen Kar Payı Avansları (Net) (-)':                                       'DIVIDEND_ADVANCES_PAID_NET',
    'Geçmiş Yıllar Kar/Zararları':                                               'RETAINED_EARNINGS',
    'Dönem Net Kar/Zararı':                                                      'PROFIT_OR_LOSS_FOR_THE_PERIOD',
    'Azınlık Payları':                                                           'NON_CONTROLLING_INTERESTS',

    'Toplam Özkaynaklar': 'TOTAL_EQUITY',

    'Toplam Kaynaklar': 'TOTAL_RESOURCES',

    'Hedge Dahil Net Yabancı Para Pozisyonu':                                    'NET_FOREIGN_CURRENCY_POSITION_INCLUDING_HEDGE',
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

                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
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

def insert_total_liabilities():
    """
    For each company & period, sum the values of
    TOTAL_LONG_TERM_LIABILITIES + TOTAL_SHORT_TERM_LIABILITIES
    and insert a new financial_fact row for TOTAL_LIABILITIES.
    """
    conn = psycopg2.connect(**DB_PARAMS)
    try:
        with conn:
            with conn.cursor() as cur:
                # 1) lookup the account_ids
                codes = [
                    'TOTAL_LIABILITIES',
                    'TOTAL_LONG_TERM_LIABILITIES',
                    'TOTAL_SHORT_TERM_LIABILITIES'
                ]
                cur.execute(
                    "SELECT code, account_id FROM account WHERE code = ANY(%s)",
                    (codes,)
                )
                acct_map: Dict[str, int] = {code: aid for code, aid in cur.fetchall()}
                total_id = acct_map['TOTAL_LIABILITIES']
                long_id  = acct_map['TOTAL_LONG_TERM_LIABILITIES']
                short_id = acct_map['TOTAL_SHORT_TERM_LIABILITIES']

                # 2) compute sums per company & period
                cur.execute(
                    """
                    SELECT
                      company_id,
                      period_id,
                      SUM(value) AS total_value
                    FROM financial_fact
                    WHERE account_id IN %s
                    GROUP BY company_id, period_id
                    """,
                    ((long_id, short_id),)
                )
                sums: Tuple[int, int, float] = cur.fetchall()

                # 3) prepare insert rows: (company_id, period_id, account_id, value)
                to_insert = [
                    (company_id, period_id, total_id, total_value)
                    for company_id, period_id, total_value in sums
                ]

                # 4) batch‐insert them
                insert_sql = """
                    INSERT INTO financial_fact
                      (company_id, period_id, account_id, value)
                    VALUES %s
                """
                execute_values(cur, insert_sql, to_insert)

        print(f"Inserted {len(to_insert)} TOTAL_LIABILITIES facts.")
    finally:
        conn.close()

