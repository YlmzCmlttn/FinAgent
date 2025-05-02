from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey, Text, inspect, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the base class for declarative models
Base = declarative_base()

class Company(Base):
    __tablename__ = 'company'
    
    company_id = Column(Integer, primary_key=True)
    ticker = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    #short_name = Column(Text)  # e.g., "Koç Holding" instead of "Koç Holding A.Ş."
    #sector = Column(Text)      # e.g., "Conglomerate", "Banking"
    #industry = Column(Text)    # e.g., "Diversified Financial Services"
    #aliases = Column(Text)     # JSON string of alternative names ["Koc", "Koch"]
    
    financial_facts = relationship("FinancialFact", back_populates="company")

class StatementType(Base):
    __tablename__ = 'statement_type'
    
    statement_type_id = Column(Integer, primary_key=True)
    code = Column(Text, nullable=False)  # e.g., 'BS', 'IS_Q', 'CF_A'
    description = Column(Text, nullable=False)  # e.g., 'Balance Sheet'
    #short_name = Column(Text)  # e.g., "BS" for Balance Sheet
    #natural_language = Column(Text)  # e.g., "how much money the company has" for Balance Sheet
    #common_terms = Column(Text)  # JSON string of related terms ["assets and liabilities", "financial position"]
    
    accounts = relationship("Account", back_populates="statement_type")
    periods = relationship("Period", back_populates="statement_type")

class Account(Base):
    __tablename__ = 'account'
    
    account_id = Column(Integer, primary_key=True)
    statement_type_id = Column(Integer, ForeignKey('statement_type.statement_type_id'), nullable=False)
    code = Column(Text, nullable=False)  # e.g., 'CURRENT_ASSETS'
    name = Column(Text, nullable=False)  # e.g., 'Dönen Varlıklar'
    #english_name = Column(Text)  # e.g., 'Current Assets'
    parent_id = Column(Integer, ForeignKey('account.account_id'))
    #category = Column(Text)  # e.g., 'Asset', 'Liability', 'Income', 'Expense'
    #natural_language = Column(Text)  # e.g., "money the company can use within a year"
    #common_terms = Column(Text)  # JSON string of related terms ["short-term assets", "liquid assets"]
    is_summary = Column(Boolean, default=False)  # True for accounts that are sums of other accounts
    
    statement_type = relationship("StatementType", back_populates="accounts")
    financial_facts = relationship("FinancialFact", back_populates="account")
    children = relationship("Account")

class Period(Base):
    __tablename__ = 'period'
    
    period_id = Column(Integer, primary_key=True)
    statement_type_id = Column(Integer, ForeignKey('statement_type.statement_type_id'), nullable=False)
    #period_end = Column(Date, nullable=False)
    frequency = Column(Text, nullable=False)  # 'Q' for Quarterly, 'A' for Annual
    year = Column(Integer, nullable=False)    # e.g., 2024
    quarter = Column(Integer)                 # 1-4 for quarters, NULL for annual
    #period_name = Column(Text, nullable=False)  # e.g., "Q1 2024", "2023 Annual"
    #natural_language = Column(Text, nullable=False)  # e.g., "first quarter of 2024", "year 2023"
    
    statement_type = relationship("StatementType", back_populates="periods")
    financial_facts = relationship("FinancialFact", back_populates="period")

class FinancialFact(Base):
    __tablename__ = 'financial_fact'
    
    fact_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('company.company_id'), nullable=False)
    period_id = Column(Integer, ForeignKey('period.period_id'), nullable=False)
    account_id = Column(Integer, ForeignKey('account.account_id'), nullable=False)
    value = Column(Numeric, nullable=False)
    #currency = Column(Text, nullable=False)
    #value_in_usd = Column(Numeric)  # Converted value in USD for comparison
    #growth_rate = Column(Numeric)   # Percentage change from previous period
    #is_estimated = Column(Boolean, default=False)  # True for estimated/projected values
    #source = Column(Text)  # Source of the data (e.g., "company_filing", "estimate")
    
    company = relationship("Company", back_populates="financial_facts")
    period = relationship("Period", back_populates="financial_facts")
    account = relationship("Account", back_populates="financial_facts")

def create_tables():
    try:
        # Create engine - using postgres service name instead of localhost
        engine = create_engine('postgresql://postgres:postgres@postgres:5432/database_trial')
        
        # Create inspector to check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # List of tables we want to create
        required_tables = ['company', 'statement_type', 'account', 'period', 'financial_fact']
        
        # Check which tables need to be created
        tables_to_create = [table for table in required_tables if table not in existing_tables]
        
        if tables_to_create:
            # Create only the missing tables
            Base.metadata.create_all(engine)
            logger.info(f"Created tables: {', '.join(tables_to_create)}")
        else:
            logger.info("All required tables already exist")
        
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

