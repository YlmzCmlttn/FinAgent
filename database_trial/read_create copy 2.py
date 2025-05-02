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
        'statement_desc': 'Bilanço'
    },
    {
        'excel_path': 'SAHOL.xlsx',
        'sheet_name': 'Bilanço',
        'company_name': 'Sahol Holding A.Ş.',
        'ticker': 'SAHOL',
        'statement_code': 'BS',
        'statement_desc': 'Bilanço'
    }
    # Add more companies here in the same format
]

# ——— Logging ———
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ——— Database Connection ———
engine = create_engine('postgresql://postgres:postgres@postgres:5432/database_trial')
Session = sessionmaker(bind=engine)

# ——— Account Hierarchy ———
ACCOUNT_HIERARCHY = {
    'Toplam Varlıklar': {
        'children': ['Toplam Dönen Varlıklar', 'Toplam Duran Varlıklar'],
        'is_summary': True
    },
    'Toplam Dönen Varlıklar': {
        'children': [],
        'is_summary': True
    },
    'Toplam Duran Varlıklar': {
        'children': [],
        'is_summary': True
    },
    'Toplam Kaynaklar': {
        'children': ['Toplam Yükümlülükler', 'Toplam Özkaynaklar'],
        'is_summary': True
    },
    'Toplam Yükümlülükler': {
        'children': ['Toplam Uzun Vadeli Yükümlülükler', 'Toplam Kısa Vadeli Yükümlülükler'],
        'is_summary': True
    },
    'Toplam Uzun Vadeli Yükümlülükler': {
        'children': [],
        'is_summary': True
    },
    'Toplam Kısa Vadeli Yükümlülükler': {
        'children': [],
        'is_summary': True
    },
    'Toplam Özkaynaklar': {
        'children': [],
        'is_summary': True
    }
}

def normalize_account_name(name):
    return name.strip().lower()

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

def get_or_create_account(session, statement_type, name, parent=None, is_summary=False):
    account = session.query(Account).filter_by(
        statement_type_id=statement_type.statement_type_id,
        name=name
    ).first()
    
    if not account:
        account = Account(
            statement_type_id=statement_type.statement_type_id,
            name=name,
            code=normalize_account_name(name),
            parent_id=parent.account_id if parent else None,
            is_summary=is_summary
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

def create_account_hierarchy(session, statement_type):
    # First create parent accounts
    for account_name, details in ACCOUNT_HIERARCHY.items():
        if not details['children']:  # Leaf nodes
            get_or_create_account(session, statement_type, account_name, is_summary=details['is_summary'])
    
    # Then create child accounts with proper parent relationships
    for account_name, details in ACCOUNT_HIERARCHY.items():
        if details['children']:  # Parent nodes
            parent = get_or_create_account(session, statement_type, account_name, is_summary=details['is_summary'])
            for child_name in details['children']:
                get_or_create_account(session, statement_type, child_name, parent=parent, is_summary=ACCOUNT_HIERARCHY[child_name]['is_summary'])

def process_company_data(config: Dict) -> None:
    """Process financial data for a single company."""
    session = Session()
    try:
        # Get or create company and statement type
        company = get_or_create_company(session, config['ticker'], config['company_name'])
        statement_type = get_or_create_statement_type(session, config['statement_code'], config['statement_desc'])
        
        # Create account hierarchy
        create_account_hierarchy(session, statement_type)
        
        # Read Excel file
        df = pd.read_excel(config['excel_path'], sheet_name=config['sheet_name'], header=0)
        df = df.rename(columns={df.columns[0]: 'account_name'})

        for col in df.columns.drop('account_name'):
            parts = col.split('/')
            if len(parts) != 2:
                continue
            try:
                year = int(parts[0])
                month = int(parts[1])
            except ValueError:
                continue

            frequency = 'Q'
            quarter = (month - 1)//3 + 1
            
            # Get or create period
            period = get_or_create_period(session, statement_type, year, quarter, frequency)

            # Process each row in the block
            block = df[['account_name', col]].dropna(subset=[col])
            for _, row in block.iterrows():
                name = row['account_name']
                if name not in ACCOUNT_HIERARCHY:
                    continue
                
                account = get_or_create_account(session, statement_type, name)
                val = row[col]
                
                # Create financial fact
                fact = FinancialFact(
                    company_id=company.company_id,
                    period_id=period.period_id,
                    account_id=account.account_id,
                    value=val
                )
                session.add(fact)
                session.commit()
                
                logger.info(f"Added FinancialFact: "
                      f"Company={config['ticker']}, "
                      f"Period={year}Q{quarter}, "
                      f"Account='{name}', "
                      f"Value={val}")
    except Exception as e:
        logger.error(f"Error processing {config['company_name']}: {str(e)}")
        session.rollback()
    finally:
        session.close()

def test_queries():
    """Run various test queries to verify data loading."""
    session = Session()
    try:
        # 1. Basic count of companies
        company_count = session.query(Company).count()
        logger.info(f"1. Total number of companies: {company_count}")

        # 2. List all companies with their tickers
        companies = session.query(Company.ticker, Company.name).all()
        logger.info("2. Companies in database:")
        for ticker, name in companies:
            logger.info(f"   - {ticker}: {name}")

        # 3. Count of financial facts per company
        facts_by_company = session.query(
            Company.ticker,
            func.count(FinancialFact.fact_id).label('fact_count')
        ).select_from(Company).join(
            FinancialFact, Company.company_id == FinancialFact.company_id
        ).group_by(Company.ticker).all()
        logger.info("3. Financial facts per company:")
        for ticker, count in facts_by_company:
            logger.info(f"   - {ticker}: {count} facts")

        # 4. Total assets (Toplam Varlıklar) for each company in the latest period
        latest_period = session.query(Period).order_by(Period.year.desc(), Period.quarter.desc()).first()
        if latest_period:
            total_assets = session.query(
                Company.ticker,
                FinancialFact.value
            ).select_from(Company).join(
                FinancialFact, Company.company_id == FinancialFact.company_id
            ).join(
                Account, FinancialFact.account_id == Account.account_id
            ).join(
                Period, FinancialFact.period_id == Period.period_id
            ).filter(
                and_(
                    Account.name == 'Toplam Varlıklar',
                    Period.period_id == latest_period.period_id
                )
            ).all()
            logger.info(f"4. Total assets in latest period ({latest_period.year}Q{latest_period.quarter}):")
            for ticker, value in total_assets:
                logger.info(f"   - {ticker}: {value:,.2f}")

        # 5. Quarterly growth of total assets
        growth_query = session.query(
            Company.ticker,
            Period.year,
            Period.quarter,
            FinancialFact.value
        ).select_from(Company).join(
            FinancialFact, Company.company_id == FinancialFact.company_id
        ).join(
            Account, FinancialFact.account_id == Account.account_id
        ).join(
            Period, FinancialFact.period_id == Period.period_id
        ).filter(
            Account.name == 'Toplam Varlıklar'
        ).order_by(Company.ticker, Period.year, Period.quarter).all()
        logger.info("5. Quarterly growth of total assets:")
        for ticker, year, quarter, value in growth_query:
            logger.info(f"   - {ticker} {year}Q{quarter}: {value:,.2f}")

        # 6. Check parent-child relationships
        parent_child = session.query(
            Account.name.label('parent'),
            Account.children
        ).filter(Account.children != None).all()
        logger.info("6. Parent-child account relationships:")
        for parent, children in parent_child:
            if children:  # Check if children is not None
                logger.info(f"   - Parent: {parent}")
                for child in children:
                    logger.info(f"     - Child: {child.name}")

        # 7. Verify all summary accounts
        summary_accounts = session.query(Account.name).filter(Account.is_summary == True).all()
        logger.info("7. Summary accounts:")
        for account in summary_accounts:
            logger.info(f"   - {account[0]}")

        # 8. Check statement types and their usage
        statement_usage = session.query(
            StatementType.code,
            StatementType.description,
            func.count(FinancialFact.fact_id).label('fact_count')
        ).select_from(StatementType).join(
            FinancialFact, StatementType.statement_type_id == FinancialFact.account_id
        ).group_by(StatementType.code, StatementType.description).all()
        logger.info("8. Statement types and their usage:")
        for code, desc, count in statement_usage:
            logger.info(f"   - {code} ({desc}): {count} facts")

        # 9. Verify data completeness for each company
        completeness = session.query(
            Company.ticker,
            func.count(distinct(Period.period_id)).label('period_count'),
            func.count(distinct(Account.account_id)).label('account_count')
        ).select_from(Company).join(
            FinancialFact, Company.company_id == FinancialFact.company_id
        ).join(
            Period, FinancialFact.period_id == Period.period_id
        ).join(
            Account, FinancialFact.account_id == Account.account_id
        ).group_by(Company.ticker).all()
        logger.info("9. Data completeness per company:")
        for ticker, periods, accounts in completeness:
            logger.info(f"   - {ticker}: {periods} periods, {accounts} accounts")

        # 10. Complex query: Check balance sheet equation (Assets = Liabilities + Equity)
        balance_check = session.query(
            Company.ticker,
            Period.year,
            Period.quarter,
            func.sum(case(
                (Account.name == 'Toplam Varlıklar', FinancialFact.value),
                (Account.name == 'Toplam Kaynaklar', -FinancialFact.value),
                else_=0
            )).label('balance_diff')
        ).select_from(Company).join(
            FinancialFact, Company.company_id == FinancialFact.company_id
        ).join(
            Account, FinancialFact.account_id == Account.account_id
        ).join(
            Period, FinancialFact.period_id == Period.period_id
        ).filter(
            or_(
                Account.name == 'Toplam Varlıklar',
                Account.name == 'Toplam Kaynaklar'
            )
        ).group_by(Company.ticker, Period.year, Period.quarter).all()
        logger.info("10. Balance sheet equation check (should be close to 0):")
        for ticker, year, quarter, diff in balance_check:
            logger.info(f"   - {ticker} {year}Q{quarter}: {diff:,.2f}")

        # 11. List all statement types
        statements = session.query(StatementType.code, StatementType.description).all()
        logger.info("11. All statement types:")
        for code, desc in statements:
            logger.info(f"   - {code}: {desc}")

        # 12. List all accounts
        accounts = session.query(Account.name, Account.code, Account.is_summary).all()
        logger.info("12. All accounts:")
        for name, code, is_summary in accounts:
            logger.info(f"   - {name} ({code}) - Summary: {is_summary}")

        # 13. List all periods
        periods = session.query(
            Period.year,
            Period.quarter,
            Period.frequency
        ).order_by(Period.year, Period.quarter).all()
        logger.info("13. All periods:")
        for year, quarter, freq in periods:
            logger.info(f"   - {year}Q{quarter} ({freq})")

        # 14. List all financial facts for a sample period
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
        ).order_by(Company.ticker, Period.year, Period.quarter, Account.name).limit(10).all()
        logger.info("14. Sample financial facts:")
        for ticker, account, year, quarter, value in sample_facts:
            logger.info(f"   - {ticker} {year}Q{quarter}: {account} = {value:,.2f}")

    except Exception as e:
        logger.error(f"Error in test queries: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        session.close()

def main():
    """Main function to process all companies."""
    # Create database tables first
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created successfully!")
    
    # Process each company
    for config in COMPANY_CONFIGS:
        logger.info(f"Processing {config['company_name']}...")
        process_company_data(config)
        logger.info(f"✅ Import complete for {config['company_name']}!")
        time.sleep(1)
    
    # Run test queries
    logger.info("Running test queries to verify data...")
    test_queries()
    logger.info("✅ Test queries completed!")

if __name__ == '__main__':
    main()
