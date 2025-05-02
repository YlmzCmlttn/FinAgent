#!/usr/bin/env python3
import pandas as pd
import calendar
from datetime import date
import logging
import time
from typing import Dict, List, Tuple
from sqlalchemy import func, and_, or_

from sqlalchemy import (
    create_engine, inspect,
    Column, Integer, Text, Numeric, Boolean, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from model import Base, Company, StatementType, Account, Period, FinancialFact, create_tables

# ——— Configuration ———
# Define company configurations
COMPANY_CONFIGS = [
    {
        'excel_path': 'KCHOL.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Koç Holding A.Ş.',
        'ticker': 'KCHOL',
        'statement_code': 'BS',
        'statement_desc': 'Balance Sheet'
    },
    {
        'excel_path': 'SAHOL.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Sahol Holding A.Ş.',
        'ticker': 'SAHOL',
        'statement_code': 'BS',
        'statement_desc': 'Balance Sheet'
    },
    {
        'excel_path': 'THYAO.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Türk Hava Yolları A.Ş.',
        'ticker': 'THYAO',
        'statement_code': 'BS',
        'statement_desc': 'Balance Sheet'
    },
    {
        'excel_path': 'TUPRS.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Türkiye Petrol Rafinerileri A.Ş.',
        'ticker': 'TUPRS',
        'statement_code': 'BS',
        'statement_desc': 'Balance Sheet'
    },
    {
        'excel_path': 'TCELL.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Türk Telekom A.Ş.',
        'ticker': 'TCELL',
        'statement_code': 'BS',
        'statement_desc': 'Balance Sheet'
    },
    {   
        'excel_path': 'TTKOM.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Türk Telekom A.Ş.',
        'ticker': 'TTKOM',
        'statement_code': 'BS',
        'statement_desc': 'Balance Sheet'
    },
    {
        'excel_path': 'SISE.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Türkiye Şişe ve Cam Fabrikaları A.Ş.',
        'ticker': 'SISE',
        'statement_code': 'BS',
        'statement_desc': 'Balance Sheet'
    },
    {
        'excel_path': 'TTRAK.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Türk Traktör ve Ziraat Makineleri A.Ş.',
        'ticker': 'TTRAK',
        'statement_code': 'BS',
        'statement_desc': 'Balance Sheet'
    },
    {
        'excel_path': 'FROTO.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Ford Otomotiv Sanayi A.Ş.',
        'ticker': 'FROTO',
        'statement_code': 'BS',
        'statement_desc': 'Balance Sheet'
    },
    {
        'excel_path': 'TOASO.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Tofaş Türk Otomobil Fabrikası A.Ş.',
        'ticker': 'TOASO',
        'statement_code': 'BS',
        'statement_desc': 'Balance Sheet'
    }    
]

# Account name translations from Turkish to English
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

# Account display names mapping
ACCOUNT_DISPLAY_NAMES = {
    'TOTAL_ASSETS': 'Total Assets',
    'TOTAL_CURRENT_ASSETS': 'Total Current Assets',
    'TOTAL_FIXED_ASSETS': 'Total Fixed Assets',
    'TOTAL_RESOURCES': 'Total Resources',
    'TOTAL_LIABILITIES': 'Total Liabilities',
    'TOTAL_LONG_TERM_LIABILITIES': 'Total Long-term Liabilities',
    'TOTAL_SHORT_TERM_LIABILITIES': 'Total Short-term Liabilities',
    'TOTAL_EQUITY': 'Total Equity'
}

# ——— Logging ———
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ——— Database Connection ———
engine = create_engine('postgresql://postgres:postgres@postgres:5432/database_trial')
Session = sessionmaker(bind=engine)

def translate_account_name(turkish_name: str) -> str:
    """Translate Turkish account name to English code."""
    return ACCOUNT_TRANSLATIONS.get(turkish_name.strip(), turkish_name)

def get_display_name(code: str) -> str:
    """Get display name for an account code."""
    return ACCOUNT_DISPLAY_NAMES.get(code, code)

def normalize_account_name(name):
    return translate_account_name(name).strip().upper()

def get_or_create_company(session, ticker, name):
    company = session.query(Company).filter_by(ticker=ticker).first()
    if not company:
        company = Company(ticker=ticker, name=name)
        session.add(company)
        session.commit()
    return company

def get_or_create_statement_type(session, code, description):
    statement_type = session.query(StatementType).filter_by(code=code).first()
    if not statement_type:
        statement_type = StatementType(code=code, description=description)
        session.add(statement_type)
        session.commit()
    return statement_type

def get_or_create_account(session, statement_type, name):
    account = session.query(Account).filter_by(
        statement_type_id=statement_type.statement_type_id,
        name=name
    ).first()
    
    if not account:
        account = Account(
            statement_type_id=statement_type.statement_type_id,
            name=name,
            code=normalize_account_name(name)
        )
        session.add(account)
        session.commit()
    return account

def get_or_create_period(session, statement_type, year, quarter, frequency):
    period = session.query(Period).filter_by(
        statement_type_id=statement_type.statement_type_id,
        year=year,
        quarter=quarter,
        frequency=frequency
    ).first()
    
    if not period:
        period = Period(
            statement_type_id=statement_type.statement_type_id,
            year=year,
            quarter=quarter,
            frequency=frequency
        )
        session.add(period)
        session.commit()
    return period

def create_accounts(session, statement_type):
    """Create all accounts."""
    # List of all accounts in uppercase code format
    accounts = [
        'TOTAL_ASSETS',
        'TOTAL_CURRENT_ASSETS',
        'TOTAL_FIXED_ASSETS',
        'TOTAL_RESOURCES',
        'TOTAL_LIABILITIES',
        'TOTAL_LONG_TERM_LIABILITIES',
        'TOTAL_SHORT_TERM_LIABILITIES',
        'TOTAL_EQUITY'
    ]
    
    # Create each account
    for account_code in accounts:
        account = get_or_create_account(session, statement_type, account_code)
        # Update the display name
        account.name = get_display_name(account_code)
        session.commit()

def process_company_data(config: Dict) -> None:
    """Process financial data for a single company."""
    session = Session()
    try:
        # Get or create company and statement type
        company = get_or_create_company(session, config['ticker'], config['company_name'])
        statement_type = get_or_create_statement_type(session, config['statement_code'], config['statement_desc'])
        
        # Create accounts
        create_accounts(session, statement_type)
        
        # Read Excel file
        logger.info(f"Reading Excel file: {config['excel_path']}")
        df = pd.read_excel(config['excel_path'], sheet_name=config['sheet_name'], header=0)
        df = df.rename(columns={df.columns[0]: 'account_name'})
        # Strip whitespace from account names in Excel
        df['account_name'] = df['account_name'].str.strip()
        # Translate account names to English codes
        df['account_name'] = df['account_name'].apply(translate_account_name)

        # List of valid accounts (in uppercase code format)
        valid_accounts = [
            'TOTAL_ASSETS',
            'TOTAL_CURRENT_ASSETS',
            'TOTAL_FIXED_ASSETS',
            'TOTAL_RESOURCES',
            'TOTAL_LIABILITIES',
            'TOTAL_LONG_TERM_LIABILITIES',
            'TOTAL_SHORT_TERM_LIABILITIES',
            'TOTAL_EQUITY'
        ]

        # Process each column (period)
        for col in df.columns.drop('account_name'):
            parts = col.split('/')
            if len(parts) != 2:
                logger.warning(f"Skipping invalid column format: {col}")
                continue
            try:
                year = int(parts[0])
                month = int(parts[1])
            except ValueError:
                logger.warning(f"Skipping invalid date format: {col}")
                continue

            frequency = 'Q'
            quarter = (month - 1)//3 + 1
            
            # Get or create period
            period = get_or_create_period(session, statement_type, year, quarter, frequency)
            #logger.info(f"Processing period: {year}Q{quarter}")

            # Process each row in the block
            block = df[['account_name', col]].dropna(subset=[col])
            #logger.info(f"Found {len(block)} non-empty rows for period {year}Q{quarter}")
            
            for _, row in block.iterrows():
                name = row['account_name']  # Already stripped
                if name not in valid_accounts:
                    #logger.debug(f"Skipping invalid account: {name}")
                    continue
                
                account = get_or_create_account(session, statement_type, name)
                val = row[col]
                
                # Check if fact already exists
                existing_fact = session.query(FinancialFact).filter_by(
                    company_id=company.company_id,
                    period_id=period.period_id,
                    account_id=account.account_id
                ).first()
                
                if existing_fact:
                    logger.debug(f"Fact already exists for {config['ticker']} {year}Q{quarter} {name}")
                    continue
                
                # Create financial fact
                fact = FinancialFact(
                    company_id=company.company_id,
                    period_id=period.period_id,
                    account_id=account.account_id,
                    value=val
                )
                session.add(fact)
                session.commit()
                
                #logger.info(f"Added FinancialFact: "
                #      f"Company={config['ticker']}, "
                #      f"Period={year}Q{quarter}, "
                #      f"Account='{name}', "
                #      f"Value={val}")

    except Exception as e:
        logger.error(f"Error processing {config['company_name']}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        session.rollback()
    finally:
        session.close()

def test_queries():
    """Run comprehensive test queries to verify data quality and relationships."""
    session = Session()
    try:
        # 1. Basic company information
        company_count = session.query(Company).count()
        logger.info(f"1. Total number of companies: {company_count}")
        
        companies = session.query(Company.ticker, Company.name, Company.company_id).all()
        logger.info("2. Companies in database:")
        for ticker, name, _ in companies:
            logger.info(f"   - {ticker}: {name}")

        # 2. Account coverage analysis
        accounts = session.query(Account.name, Account.code).all()
        logger.info("3. All accounts:")
        for name, code in accounts:
            logger.info(f"   - {name} ({code})")

        # 3. Period coverage analysis
        periods = session.query(
            Period.year,
            Period.quarter,
            Period.frequency
        ).order_by(Period.year, Period.quarter).all()
        logger.info("4. All periods:")
        for year, quarter, freq in periods:
            logger.info(f"   - {year}Q{quarter} ({freq})")

        # 4. Financial facts analysis
        facts_count = session.query(func.count(FinancialFact.fact_id)).scalar()
        logger.info(f"5. Total number of financial facts: {facts_count}")

        # 5. Data completeness check
        logger.info("6. Data completeness check:")
        for ticker, name, company_id in companies:
            # Count facts per company
            facts_per_company = session.query(func.count(FinancialFact.fact_id)).filter(
                FinancialFact.company_id == company_id
            ).scalar()
            
            # Count periods with data
            periods_with_data = session.query(func.count(func.distinct(Period.period_id))).join(
                FinancialFact, Period.period_id == FinancialFact.period_id
            ).filter(
                FinancialFact.company_id == company_id
            ).scalar()
            
            logger.info(f"   - {ticker}: {facts_per_company} facts across {periods_with_data} periods")

        # 6. Sample financial analysis
        logger.info("7. Sample financial analysis:")
        for ticker, name, company_id in companies:
            # Get latest total assets
            latest_assets = session.query(
                FinancialFact.value,
                Period.year,
                Period.quarter
            ).join(
                Account, FinancialFact.account_id == Account.account_id
            ).join(
                Period, FinancialFact.period_id == Period.period_id
            ).filter(
                FinancialFact.company_id == company_id,
                Account.name == 'TOTAL_ASSETS'
            ).order_by(
                Period.year.desc(),
                Period.quarter.desc()
            ).first()
            
            if latest_assets:
                logger.info(f"   - {ticker} latest total assets ({latest_assets[1]}Q{latest_assets[2]}): {latest_assets[0]:,.2f}")

        # 7. Data consistency check
        logger.info("8. Data consistency check:")
        for ticker, name, company_id in companies:
            # Check if assets = liabilities + equity
            latest_period = session.query(
                Period.period_id,
                Period.year,
                Period.quarter
            ).join(
                FinancialFact, Period.period_id == FinancialFact.period_id
            ).filter(
                FinancialFact.company_id == company_id
            ).order_by(
                Period.year.desc(),
                Period.quarter.desc()
            ).first()
            
            if latest_period:
                assets = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_ASSETS'
                ).scalar()
                
                liabilities = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_LIABILITIES'
                ).scalar()
                
                equity = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_EQUITY'
                ).scalar()
                
                if all(v is not None for v in [assets, liabilities, equity]):
                    diff = abs(assets - (liabilities + equity))
                    logger.info(f"   - {ticker} {latest_period[1]}Q{latest_period[2]}: "
                              f"Assets ({assets:,.2f}) = Liabilities ({liabilities:,.2f}) + Equity ({equity:,.2f}) "
                              f"| Difference: {diff:,.2f}")

        # 8. Sample detailed financial facts
        logger.info("9. Sample detailed financial facts:")
        sample_facts = session.query(
            Company.ticker,
            Account.name,
            Period.year,
            Period.quarter,
            FinancialFact.value
        ).select_from(Company).join(
            FinancialFact, Company.company_id == FinancialFact.company_id
        ).join(
            Account, FinancialFact.account_id == Account.account_id
        ).join(
            Period, FinancialFact.period_id == Period.period_id
        ).order_by(
            Company.ticker,
            Period.year.desc(),
            Period.quarter.desc()
        ).limit(10).all()
        
        for ticker, account, year, quarter, value in sample_facts:
            logger.info(f"   - {ticker} {year}Q{quarter}: {account} = {value:,.2f}")

        # 9. Growth Analysis
        logger.info("10. Growth Analysis:")
        for ticker, name, company_id in companies:
            # Get total assets for last 4 quarters
            recent_assets = session.query(
                FinancialFact.value,
                Period.year,
                Period.quarter
            ).join(
                Account, FinancialFact.account_id == Account.account_id
            ).join(
                Period, FinancialFact.period_id == Period.period_id
            ).filter(
                FinancialFact.company_id == company_id,
                Account.name == 'TOTAL_ASSETS'
            ).order_by(
                Period.year.desc(),
                Period.quarter.desc()
            ).limit(4).all()
            
            if len(recent_assets) >= 2:
                latest = recent_assets[0]
                previous = recent_assets[1]
                growth = ((latest[0] - previous[0]) / previous[0]) * 100
                logger.info(f"   - {ticker} Total Assets Growth: "
                          f"{previous[1]}Q{previous[2]} to {latest[1]}Q{latest[2]}: {growth:.2f}%")

        # 10. Financial Ratios
        logger.info("11. Financial Ratios:")
        for ticker, name, company_id in companies:
            # Get latest period data
            latest_period = session.query(
                Period.period_id,
                Period.year,
                Period.quarter
            ).join(
                FinancialFact, Period.period_id == FinancialFact.period_id
            ).filter(
                FinancialFact.company_id == company_id
            ).order_by(
                Period.year.desc(),
                Period.quarter.desc()
            ).first()
            
            if latest_period:
                # Get required values
                current_assets = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_CURRENT_ASSETS'
                ).scalar()
                
                current_liabilities = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_SHORT_TERM_LIABILITIES'
                ).scalar()
                
                total_liabilities = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_LIABILITIES'
                ).scalar()
                
                total_assets = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_ASSETS'
                ).scalar()
                
                if all(v is not None for v in [current_assets, current_liabilities, total_liabilities, total_assets]):
                    # Current Ratio
                    current_ratio = current_assets / current_liabilities
                    # Debt Ratio
                    debt_ratio = total_liabilities / total_assets
                    
                    logger.info(f"   - {ticker} {latest_period[1]}Q{latest_period[2]}:")
                    logger.info(f"     Current Ratio: {current_ratio:.2f}")
                    logger.info(f"     Debt Ratio: {debt_ratio:.2f}")

        # 11. Asset Composition Analysis
        logger.info("12. Asset Composition Analysis:")
        for ticker, name, company_id in companies:
            latest_period = session.query(
                Period.period_id,
                Period.year,
                Period.quarter
            ).join(
                FinancialFact, Period.period_id == FinancialFact.period_id
            ).filter(
                FinancialFact.company_id == company_id
            ).order_by(
                Period.year.desc(),
                Period.quarter.desc()
            ).first()
            
            if latest_period:
                current_assets = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_CURRENT_ASSETS'
                ).scalar()
                
                fixed_assets = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_FIXED_ASSETS'
                ).scalar()
                
                total_assets = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_ASSETS'
                ).scalar()
                
                if all(v is not None for v in [current_assets, fixed_assets, total_assets]):
                    current_assets_pct = (current_assets / total_assets) * 100
                    fixed_assets_pct = (fixed_assets / total_assets) * 100
                    
                    logger.info(f"   - {ticker} {latest_period[1]}Q{latest_period[2]}:")
                    logger.info(f"     Current Assets: {current_assets_pct:.1f}%")
                    logger.info(f"     Fixed Assets: {fixed_assets_pct:.1f}%")

        # 12. Liability Structure Analysis
        logger.info("13. Liability Structure Analysis:")
        for ticker, name, company_id in companies:
            latest_period = session.query(
                Period.period_id,
                Period.year,
                Period.quarter
            ).join(
                FinancialFact, Period.period_id == FinancialFact.period_id
            ).filter(
                FinancialFact.company_id == company_id
            ).order_by(
                Period.year.desc(),
                Period.quarter.desc()
            ).first()
            
            if latest_period:
                short_term_liabilities = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_SHORT_TERM_LIABILITIES'
                ).scalar()
                
                long_term_liabilities = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_LONG_TERM_LIABILITIES'
                ).scalar()
                
                total_liabilities = session.query(FinancialFact.value).join(
                    Account, FinancialFact.account_id == Account.account_id
                ).filter(
                    FinancialFact.period_id == latest_period[0],
                    FinancialFact.company_id == company_id,
                    Account.name == 'TOTAL_LIABILITIES'
                ).scalar()
                
                if all(v is not None for v in [short_term_liabilities, long_term_liabilities, total_liabilities]):
                    short_term_pct = (short_term_liabilities / total_liabilities) * 100
                    long_term_pct = (long_term_liabilities / total_liabilities) * 100
                    
                    logger.info(f"   - {ticker} {latest_period[1]}Q{latest_period[2]}:")
                    logger.info(f"     Short-term Liabilities: {short_term_pct:.1f}%")
                    logger.info(f"     Long-term Liabilities: {long_term_pct:.1f}%")

    except Exception as e:
        logger.error(f"Error in test queries: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        session.close()

def read_create_tables():
    """Main function to process all companies."""
    # Create database tables first
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created successfully!")
    
    # Process each company
    for config in COMPANY_CONFIGS:
        process_company_data(config)
        time.sleep(1)

def main():
    """Main function to process all companies."""
    # Create database tables first
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created successfully!")
    
    # Process each company
    for config in COMPANY_CONFIGS:
        process_company_data(config)
        time.sleep(1)
    # Run test queries
    logger.info("Running test queries to verify data...")
    test_queries()
    logger.info("✅ Test queries completed!")

if __name__ == '__main__':
    read_create_tables()
