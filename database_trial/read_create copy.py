#!/usr/bin/env python3
import pandas as pd
import calendar
from datetime import date
import logging

from sqlalchemy import (
    create_engine, inspect,
    Column, Integer, Text, Numeric, Boolean, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# ——— Configuration ———
EXCEL_PATH     = 'KCHOL.xlsx'
SHEET_NAME     = 'Bilanço'
COMPANY_NAME   = 'Koç Holding A.Ş.'
TICKER         = 'KCHOL'
STATEMENT_CODE = 'BS'
STATEMENT_DESC = 'Bilanço'
ACCOUNT_NAMES  = [
    'Dönen Varlıklar',
    'Maddi Duran Varlıklar',
    'Yabancı Para Pozisyonu',
    # … add more exactly as in your sheet …
]
DB_URL = 'postgresql://postgres:postgres@postgres:5432/database_trial'
# ——————————————————

# ——— Logging ———
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ——— Models ———
Base = declarative_base()

class Company(Base):
    __tablename__ = 'company'
    company_id = Column(Integer, primary_key=True)
    ticker     = Column(Text, nullable=False, unique=True)
    name       = Column(Text, nullable=False)
    financial_facts = relationship("FinancialFact", back_populates="company")

class StatementType(Base):
    __tablename__ = 'statement_type'
    statement_type_id = Column(Integer, primary_key=True)
    code        = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    accounts    = relationship("Account", back_populates="statement_type")
    periods     = relationship("Period", back_populates="statement_type")

class Account(Base):
    __tablename__ = 'account'
    account_id        = Column(Integer, primary_key=True)
    statement_type_id = Column(Integer, ForeignKey('statement_type.statement_type_id'), nullable=False)
    code              = Column(Text, nullable=False)
    name              = Column(Text, nullable=False)
    is_summary        = Column(Boolean, default=False)
    statement_type    = relationship("StatementType", back_populates="accounts")
    financial_facts   = relationship("FinancialFact", back_populates="account")

class Period(Base):
    __tablename__ = 'period'
    period_id         = Column(Integer, primary_key=True)
    statement_type_id = Column(Integer, ForeignKey('statement_type.statement_type_id'), nullable=False)
    frequency         = Column(Text, nullable=False)  # 'Q'
    year              = Column(Integer, nullable=False)
    quarter           = Column(Integer, nullable=False)
    statement_type    = relationship("StatementType", back_populates="periods")
    financial_facts   = relationship("FinancialFact", back_populates="period")

class FinancialFact(Base):
    __tablename__ = 'financial_fact'
    fact_id    = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('company.company_id'), nullable=False)
    period_id  = Column(Integer, ForeignKey('period.period_id'), nullable=False)
    account_id = Column(Integer, ForeignKey('account.account_id'), nullable=False)
    value      = Column(Numeric, nullable=False)
    company    = relationship("Company", back_populates="financial_facts")
    period     = relationship("Period", back_populates="financial_facts")
    account    = relationship("Account", back_populates="financial_facts")

# ——— Helpers ———
def create_tables(engine):
    inspector = inspect(engine)
    existing = inspector.get_table_names()
    needed = ['company','statement_type','account','period','financial_fact']
    if any(t not in existing for t in needed):
        Base.metadata.create_all(engine)
        logger.info("Created missing tables.")
    else:
        logger.info("All tables already exist.")

def get_or_create(session, model, defaults=None, **kwargs):
    """
    Idempotent lookup or creation, with a print before creating.
    """
    obj = session.query(model).filter_by(**kwargs).one_or_none()
    if obj:
        return obj

    # prepare creation parameters
    params = dict(kwargs)
    if defaults:
        params.update(defaults)

    # show what we will create
    print(f"→ Will create {model.__name__}: {params}")

    # create, add, flush so PK is assigned
    obj = model(**params)
    session.add(obj)
    session.flush()
    return obj

# ——— Main Import Logic ———
def main():
    # 1) Prep DB
    engine = create_engine(DB_URL)
    create_tables(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 2) Master rows
    company   = get_or_create(session, Company,
                              ticker=TICKER,
                              name=COMPANY_NAME)
    stmt_type = get_or_create(session, StatementType,
                              code=STATEMENT_CODE,
                              defaults={'description': STATEMENT_DESC})

    # accounts map name→Account instance
    accounts = {}
    for name in ACCOUNT_NAMES:
        acct = get_or_create(
            session,
            Account,
            statement_type_id=stmt_type.statement_type_id,
            code=name.upper().replace(' ','_'),
            defaults={'name': name}
        )
        accounts[name] = acct

    session.commit()

    # 3) Read Excel
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, header=0)
    df = df.rename(columns={df.columns[0]: 'account_name'})

    # 4) Loop each “YYYY/M” header and import
    for col in df.columns.drop('account_name'):
        parts = col.split('/')
        if len(parts) != 2:
            continue
        try:
            year  = int(parts[0])
            month = int(parts[1])
        except ValueError:
            continue

        frequency = 'Q'
        quarter   = (month - 1)//3 + 1

        # upsert Period by (statement_type, year, quarter)
        period = get_or_create(
            session,
            Period,
            statement_type_id=stmt_type.statement_type_id,
            year=year,
            quarter=quarter,
            defaults={'frequency': frequency}
        )

        # 5) Insert facts WITH a print before each
        block = df[['account_name', col]].dropna(subset=[col])
        for _, row in block.iterrows():
            name = row['account_name'].strip()
            if name not in accounts:
                continue
            val = row[col]
            print(f"→ Will add FinancialFact: "
                  f"Company={TICKER}, "
                  f"Period={year}Q{quarter}, "
                  f"Account='{name}', "
                  f"Value={val}")
            session.add(FinancialFact(
                company_id=company.company_id,
                period_id=period.period_id,
                account_id=accounts[name].account_id,
                value=val
            ))

    session.commit()
    session.close()
    print("✅ Import complete!")

if __name__ == '__main__':
    main()
