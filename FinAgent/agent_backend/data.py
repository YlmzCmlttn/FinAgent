# --- SAMPLE DATA ---
SAMPLE_ACCOUNTS = [

    ##### CURRENT ASSETS
    {
        'code':        'CASH_AND_CASH_EQUIVALENTS',
        'name':        'Cash and Cash Equivalents',
        'description': (
            'Cash on hand, bank balances, and highly liquid short-term investments '
            'with original maturities of three months or less.'
        )
    },
    {
        'code':        'CASH_ACCOUNTS_REAL_ESTATE_PROJECTS',
        'name':        'Cash Accounts for Real Estate Projects',
        'description': (
            'Cash accounts specifically established for financing and operations '
            'of real estate development projects.'
        )
    },
    {
        'code':        'FINANCIAL_INVESTMENTS_CURRENT',
        'name':        'Current Financial Investments',
        'description': (
            'Financial investments expected to be realized within one year, '
            'such as marketable securities and short-term deposits.'
        )
    },
    {
        'code':        'CURRENT_PLEDGED_FINANCIAL_ASSETS',
        'name':        'Current Pledged Financial Assets',
        'description': (
            'Financial assets provided as collateral for obligations, expected '
            'to be released or returned within one year.'
        )
    },
    {
        'code':        'CURRENT_TRADE_RECEIVABLES',
        'name':        'Current Trade Receivables',
        'description': 'Trade receivables expected to be collected within one year.'
    },
    {
        'code':        'CURRENT_FINANCIAL_SECTOR_RECEIVABLES',
        'name':        'Current Receivables from Financial Sector Activities',
        'description': (
            'Receivables from banking and financial services operations due '
            'within one year.'
        )
    },
    {
        'code':        'CENTRAL_BANK_OF_TURKEY_ACCOUNT',
        'name':        'Central Bank of the Republic of Turkey Account',
        'description': 'Cash balances held at the Central Bank of the Republic of Turkey.'
    },
    {
        'code':        'CURRENT_OTHER_RECEIVABLES',
        'name':        'Current Other Receivables',
        'description': (
            'Various receivables expected to be settled within one year that '
            'are not separately classified elsewhere.'
        )
    },
    {
        'code':        'CURRENT_ASSETS_FROM_CUSTOMER_CONTRACTS',
        'name':        'Current Assets from Customer Contracts',
        'description': (
            'Contract assets arising from customer agreements, expected to be '
            'realized within one year.'
        )
    },
    {
        'code':        'CURRENT_FINANCIAL_ASSETS_FROM_CONCESSION_CONTRACTS',
        'name':        'Current Financial Assets Related to Concession Contracts',
        'description': (
            'Financial assets from concession agreements due within one year.'
        )
    },
    {
        'code':        'CURRENT_DERIVATIVE_INSTRUMENTS',
        'name':        'Current Derivative Instruments',
        'description': (
            'Derivative financial instruments held for hedging or trading with '
            'maturities within one year.'
        )
    },
    {
        'code':        'CURRENT_INVENTORIES',
        'name':        'Current Inventories',
        'description': 'Inventories expected to be sold or used within one year.'
    },
    {
        'code':        'CURRENT_INVENTORIES_IN_PROGRESS',
        'name':        'Current Inventories in Progress',
        'description': 'Work-in-progress inventories related to ongoing operations.'
    },
    {
        'code':        'CURRENT_BIOLOGICAL_ASSETS',
        'name':        'Current Biological Assets',
        'description': (
            'Biological assets such as livestock or crops expected to be harvested '
            'or sold within one year.'
        )
    },
    {
        'code':        'CURRENT_PREPAID_EXPENSES',
        'name':        'Current Prepaid Expenses',
        'description': 'Prepayments for expenses that will be recognized within one year.'
    },
    {
        'code':        'CURRENT_DEFERRED_INSURANCE_PRODUCTION_COSTS',
        'name':        'Current Deferred Insurance Production Costs',
        'description': (
            'Costs incurred for insurance production activities that are deferred '
            'and amortized within one year.'
        )
    },
    {
        'code':        'CURRENT_TAX_ASSETS',
        'name':        'Current Tax Assets',
        'description': (
            'Assets related to current period income taxes, including refundable '
            'tax credits.'
        )
    },
    {
        'code':        'CURRENT_NON_CASH_FREELY_USABLE_COLLATERALS',
        'name':        'Current Non-cash Freely Usable Collaterals',
        'description': (
            'Non-cash collateral assets available for use within one year.'
        )
    },
    {
        'code':        'OTHER_CURRENT_ASSETS',
        'name':        'Other Current Assets',
        'description': 'Various current assets not separately classified elsewhere.'
    },
    {
        'code':        'CURRENT_ASSETS_HELD_FOR_SALE',
        'name':        'Current Assets Held for Sale',
        'description': (
            'Assets classified as held for sale when sale is highly probable '
            'within one year.'
        )
    },
    {
        'code':        'CURRENT_ASSETS_HELD_FOR_DISTRIBUTION_TO_OWNERS',
        'name':        'Current Assets Held for Distribution to Owners',
        'description': (
            'Assets intended for distribution directly to owners within one year.'
        )
    },
    {
        'code':        'TOTAL_CURRENT_ASSETS',
        'name':        'Total Current Assets',
        'description': (
            'Assets expected to be converted to cash or consumed within one year, '
            'including cash, receivables, and inventory.'
        )
    },
    ##### FIXED ASSETS
    {
        'code':        'FINANCIAL_INVESTMENTS_FIXED',
        'name':        'Fixed Financial Investments',
        'description': (
            'Long-term financial investments held for more than one year, '
            'such as equity holdings and debt instruments not readily convertible to cash.'
        )
    },
    {
        'code':        'FIXED_INVESTMENTS_IN_ASSOCIATES_JOINT_VENTURES_AND_SUBSIDIARIES',
        'name':        'Investments in Associates, Joint Ventures, and Subsidiaries (Fixed)',
        'description': (
            'Long-term investments in associates, joint ventures, and subsidiaries '
            'accounted for under the equity method.'
        )
    },
    {
        'code':        'FIXED_TRADE_RECEIVABLES',
        'name':        'Fixed Trade Receivables',
        'description': 'Trade receivables expected to be collected beyond one year.'
    },
    {
        'code':        'FIXED_FINANCIAL_SECTOR_RECEIVABLES',
        'name':        'Fixed Receivables from Financial Sector Activities',
        'description': (
            'Receivables from banking and financial services operations due beyond one year.'
        )
    },
    {
        'code':        'FIXED_OTHER_RECEIVABLES',
        'name':        'Fixed Other Receivables',
        'description': (
            'Various receivables expected to be settled beyond one year that are not '
            'separately classified elsewhere.'
        )
    },
    {
        'code':        'FIXED_ASSETS_FROM_CUSTOMER_CONTRACTS',
        'name':        'Fixed Assets from Customer Contracts',
        'description': (
            'Contract assets arising from customer agreements expected to be realized '
            'beyond one year.'
        )
    },
    {
        'code':        'FIXED_FINANCIAL_ASSETS_FROM_CONCESSION_CONTRACTS',
        'name':        'Fixed Financial Assets Related to Concession Contracts',
        'description': (
            'Financial assets arising from concession agreements with maturities '
            'exceeding one year.'
        )
    },
    {
        'code':        'FIXED_DERIVATIVE_INSTRUMENTS',
        'name':        'Fixed Derivative Instruments',
        'description': (
            'Derivative financial instruments held for hedging or investment with maturities '
            'beyond one year.'
        )
    },
    {
        'code':        'FIXED_INVENTORIES',
        'name':        'Fixed Inventories',
        'description': 'Inventories held for long-term projects or purposes exceeding one year.'
    },
    {
        'code':        'FIXED_EQUITY_METHOD_INVESTMENTS',
        'name':        'Equity Method Investments (Fixed)',
        'description': (
            'Long-term investments in which the equity method is applied, such as '
            'significant influence stakes.'
        )
    },
    {
        'code':        'FIXED_BIOLOGICAL_ASSETS',
        'name':        'Fixed Biological Assets',
        'description': 'Biological assets such as crops and livestock held for more than one year.'
    },
    {
        'code':        'FIXED_INVESTMENT_PROPERTIES',
        'name':        'Investment Properties (Fixed)',
        'description': (
            'Properties held to earn rentals or for capital appreciation rather than use '
            'in production or supply of goods or services.'
        )
    },
    {
        'code':        'FIXED_INVESTMENT_PROPERTIES_IN_PROGRESS',
        'name':        'Investment Properties in Progress (Fixed)',
        'description': 'Investment properties under development or construction.'
    },
    {
        'code':        'FIXED_TANGIBLE_ASSETS',
        'name':        'Fixed Tangible Assets',
        'description': (
            'Physical assets held for use in production or supply of goods and services, '
            'with useful life beyond one year.'
        )
    },
    {
        'code':        'FIXED_RIGHT_OF_USE_ASSETS',
        'name':        'Right-of-Use Assets (Fixed)',
        'description': (
            'Assets representing a lessee’s right to use an underlying asset for the '
            'lease term.'
        )
    },
    {
        'code':        'FIXED_INTANGIBLE_ASSETS',
        'name':        'Fixed Intangible Assets',
        'description': (
            'Non-physical assets with long-term benefits, such as patents, trademarks, and goodwill.'
        )
    },
    {
        'code':        'FIXED_PREPAID_EXPENSES',
        'name':        'Fixed Prepaid Expenses',
        'description': 'Prepayments for expenses that will be recognized beyond one year.'
    },
    {
        'code':        'FIXED_DEFERRED_TAX_ASSETS',
        'name':        'Fixed Deferred Tax Assets',
        'description': (
            'Deferred tax assets expected to be realized beyond one year arising from '
            'temporary differences and tax loss carryforwards.'
        )
    },
    {
        'code':        'FIXED_CURRENT_PERIOD_TAX_ASSETS',
        'name':        'Current Period Tax Assets (Fixed)',
        'description': (
            'Non-current assets related to current period tax refunds or credits expected '
            'to be realized beyond one year.'
        )
    },
    {
        'code':        'FIXED_NON_CASH_FREELY_USABLE_COLLATERALS',
        'name':        'Fixed Non-cash Freely Usable Collaterals',
        'description': (
            'Non-cash collateral assets with maturities beyond one year that can be '
            'freely used or liquidated.'
        )
    },
    {
        'code':        'OTHER_FIXED_ASSETS',
        'name':        'Other Fixed Assets',
        'description': 'Various fixed assets not classified elsewhere, expected to provide economic benefits beyond one year.'
    },
    {
        'code':        'TOTAL_FIXED_ASSETS',
        'name':        'Total Fixed Assets',
        'description': 'The sum of all non-current assets held by the company, including tangible, intangible, and long-term financial assets.'
    },
    {
        'code':        'TOTAL_ASSETS',
        'name':        'Total Assets',
        'description': 'The sum of all assets owned by the company, including current and non-current assets; excludes liabilities.'
    },

    ##### LIABILITIES

    ##### SHORT TERM LIABILITIES
    {
        'code':        'SHORT_TERM_FINANCIAL_BORROWINGS',
        'name':        'Short-term Financial Borrowings',
        'description': 'Short-term obligations from debt instruments (e.g. bank loans, commercial paper) due within one year.'
    },
    {
        'code':        'SHORT_TERM_OTHER_FINANCIAL_LIABILITIES',
        'name':        'Other Short-term Financial Liabilities',
        'description': 'Various short-term financial obligations not classified as borrowings or derivatives.'
    },
    {
        'code':        'SHORT_TERM_TRADE_PAYABLES',
        'name':        'Short-term Trade Payables',
        'description': 'Amounts owed to suppliers for goods and services, to be settled within one year.'
    },
    {
        'code':        'SHORT_TERM_FINANCIAL_SECTOR_LIABILITIES',
        'name':        'Short-term Liabilities from Financial Sector Activities',
        'description': 'Obligations arising from banking and financial services operations, due within one year.'
    },
    {
        'code':        'SHORT_TERM_EMPLOYEE_BENEFITS_LIABILITIES',
        'name':        'Short-term Employee Benefits Liabilities',
        'description': 'Obligations to employees for salaries, pensions, and other benefits payable within one year.'
    },
    {
        'code':        'SHORT_TERM_OTHER_BORROWINGS',
        'name':        'Other Short-term Borrowings',
        'description': 'Various non-financial obligations expected to be settled within one year.'
    },
    {
        'code':        'SHORT_TERM_LIABILITIES_FROM_CUSTOMER_CONTRACTS',
        'name':        'Short-term Liabilities from Customer Contracts',
        'description': 'Unearned revenue and other contract liabilities expected to be recognized as revenue within one year.'
    },
    {
        'code':        'SHORT_TERM_LIABILITIES_FROM_EQUITY_METHOD_INVESTMENTS',
        'name':        'Short-term Liabilities from Equity Method Investments',
        'description': 'Obligations related to investments accounted for under the equity method, due within one year.'
    },
    {
        'code':        'SHORT_TERM_DERIVATIVE_LIABILITIES',
        'name':        'Short-term Derivative Liabilities',
        'description': 'Obligations under derivative contracts (e.g. forwards, options) with maturities within one year.'
    },
    {
        'code':        'SHORT_TERM_GOVERNMENT_GRANTS_AND_AIDS',
        'name':        'Short-term Government Grants and Aids',
        'description': 'Liabilities recognized for government grants and aid to be repaid or fulfilled within one year.'
    },
    {
        'code':        'SHORT_TERM_DEFERRED_INCOME',
        'name':        'Short-term Deferred Income',
        'description': 'Advance payments received for goods or services expected to be delivered within one year.'
    },
    {
        'code':        'SHORT_TERM_INCOME_TAX_LIABILITIES',
        'name':        'Short-term Income Tax Liabilities',
        'description': 'Income taxes payable to tax authorities for the current period, due within one year.'
    },
    {
        'code':        'SHORT_TERM_PROVISIONS',
        'name':        'Short-term Provisions',
        'description': 'Reserves for liabilities such as warranties, restructurings, and legal claims expected to be settled within one year.'
    },
    {
        'code':        'OTHER_SHORT_TERM_LIABILITIES',
        'name':        'Other Short-term Liabilities',
        'description': 'Various short-term obligations not classified elsewhere.'
    },
    {
        'code':        'SHORT_TERM_LIABILITIES_RELATING_TO_ASSETS_CLASSIFIED_AS_HELD_FOR_SALE',
        'name':        'Short-term Liabilities Relating to Assets Classified as Held for Sale',
        'description': 'Obligations directly associated with assets classified as held for sale, expected to be settled within one year.'
    },
    {
        'code':        'SHORT_TERM_LIABILITIES_RELATING_TO_ASSETS_HELD_FOR_DISTRIBUTION_TO_OWNERS',
        'name':        'Short-term Liabilities Relating to Assets Held for Distribution to Owners',
        'description': 'Obligations directly associated with assets held for distribution to owners, expected to be settled within one year.'
    },
    {
        'code':        'TOTAL_SHORT_TERM_LIABILITIES',
        'name':        'Total Short-term Liabilities',
        'description': 'The sum of all liabilities expected to be settled within one year.'
    },

    ##### LONG TERM LIABILITIES

    {
        'code':        'LONG_TERM_FINANCIAL_BORROWINGS',
        'name':        'Long-term Financial Borrowings',
        'description': 'Obligations from debt instruments (e.g. bonds, loans) maturing beyond one year.'
    },
    {
        'code':        'LONG_TERM_OTHER_FINANCIAL_LIABILITIES',
        'name':        'Other Long-term Financial Liabilities',
        'description': 'Non-borrowing financial obligations due beyond one year, such as lease liabilities.'
    },
    {
        'code':        'LONG_TERM_TRADE_PAYABLES',
        'name':        'Long-term Trade Payables',
        'description': 'Amounts owed to suppliers for goods and services payable after more than one year.'
    },
    {
        'code':        'LONG_TERM_FINANCIAL_SECTOR_LIABILITIES',
        'name':        'Long-term Liabilities from Financial Sector Activities',
        'description': 'Obligations arising from banking and financial services operations due beyond one year.'
    },
    {
        'code':        'LONG_TERM_EMPLOYEE_BENEFITS_LIABILITIES',
        'name':        'Long-term Employee Benefits Liabilities',
        'description': 'Obligations to employees for pensions and other benefits payable after one year.'
    },
    {
        'code':        'LONG_TERM_OTHER_BORROWINGS',
        'name':        'Other Long-term Borrowings',
        'description': 'Various non-financial obligations expected to be settled after more than one year.'
    },
    {
        'code':        'LONG_TERM_LIABILITIES_FROM_CUSTOMER_CONTRACTS',
        'name':        'Long-term Liabilities from Customer Contracts',
        'description': 'Contract liabilities (unearned revenue) expected to be recognized after one year.'
    },
    {
        'code':        'LONG_TERM_GOVERNMENT_GRANTS_AND_AIDS',
        'name':        'Long-term Government Grants and Aids',
        'description': 'Deferred liabilities for government grants repayable or fulfilled beyond one year.'
    },
    {
        'code':        'LONG_TERM_LIABILITIES_FROM_EQUITY_METHOD_INVESTMENTS',
        'name':        'Long-term Liabilities from Equity Method Investments',
        'description': 'Obligations related to equity-accounted investments due after one year.'
    },
    {
        'code':        'LONG_TERM_DERIVATIVE_LIABILITIES',
        'name':        'Long-term Derivative Liabilities',
        'description': 'Obligations under derivative contracts (e.g. swaps, options) maturing beyond one year.'
    },
    {
        'code':        'LONG_TERM_DEFERRED_INCOME',
        'name':        'Long-term Deferred Income',
        'description': 'Advance payments received for goods or services to be delivered after one year.'
    },
    {
        'code':        'LONG_TERM_PROVISIONS',
        'name':        'Long-term Provisions',
        'description': 'Reserves for liabilities such as warranties or restructurings expected to be settled after one year.'
    },
    {
        'code':        'LONG_TERM_CURRENT_PERIOD_TAX_LIABILITIES',
        'name':        'Current Period Tax Liabilities (Long-term)',
        'description': 'Tax liabilities for the current period expected to be settled beyond one year.'
    },
    {
        'code':        'LONG_TERM_DEFERRED_TAX_LIABILITIES',
        'name':        'Deferred Tax Liabilities (Long-term)',
        'description': 'Tax obligations deferred to future periods, expected to be settled after one year.'
    },
    {
        'code':        'OTHER_LONG_TERM_LIABILITIES',
        'name':        'Other Long-term Liabilities',
        'description': 'Various long-term obligations not classified elsewhere.'
    },
    {
        'code':        'TOTAL_LONG_TERM_LIABILITIES',
        'name':        'Total Long-term Liabilities',
        'description': 'The sum of all liabilities due beyond one year.'
    },

    {'code':'TOTAL_LIABILITIES','name':'Total Liabilities','description':'The sum of all financial obligations owed (includes short- and long-term liabilities; excludes equity).'},

    ##### EQUITY   
    {
        'code':        'EQUITY_ATTRIBUTABLE_TO_OWNERS_OF_PARENT',
        'name':        'Equity Attributable to Owners of the Parent',
        'description': 'The portion of total equity that is attributable to the parent company’s shareholders.'
    },
    {
        'code':        'PAID_IN_CAPITAL',
        'name':        'Paid-in Capital',
        'description': 'Capital contributed by shareholders in exchange for shares at issuance.'
    },
    {
        'code':        'CAPITAL_ADJUSTMENT_DIFFERENCES',
        'name':        'Capital Adjustment Differences',
        'description': 'Adjustments to share capital arising from inflation, currency translation, or other statutory revaluations.'
    },
    {
        'code':        'MERGER_EQUALISATION_ACCOUNT',
        'name':        'Merger Equalisation Account',
        'description': 'Adjustment account used to eliminate differences arising from mergers under statutory accounting rules.'
    },
    {
        'code':        'ADDITIONAL_PAID_IN_CAPITAL',
        'name':        'Additional Paid-in Capital',
        'description': 'Amounts received from shareholders in excess of the nominal value of shares issued.'
    },
    {
        'code':        'CAPITAL_ADVANCE',
        'name':        'Capital Advance',
        'description': 'Funds received from shareholders for future capital increases or share issuances.'
    },
    {
        'code':        'TREASURY_SHARES',
        'name':        'Treasury Shares',
        'description': 'Shares repurchased by the company, presented as a deduction from total equity.'
    },
    {
        'code':        'RECIPROCAL_INVESTMENT_CAPITAL_ADJUSTMENT',
        'name':        'Reciprocal Investment Capital Adjustment',
        'description': 'Elimination of capital accounts in cases of mutual shareholding between group companies.'
    },
    {
        'code':        'SHARE_PREMIUMS',
        'name':        'Share Premiums (Discounts)',
        'description': 'Premiums or discounts arising on issuance of shares above or below their nominal value.'
    },
    {
        'code':        'EFFECT_OF_BUSINESS_COMBINATIONS_UNDER_COMMON_CONTROL',
        'name':        'Effect of Business Combinations under Common Control',
        'description': 'Equity adjustments arising from mergers or acquisitions between entities under common control.'
    },
    {
        'code':        'SHARE_BASED_PAYMENTS',
        'name':        'Share-based Payments',
        'description': 'Equity instruments granted to employees or other parties as compensation or incentives.'
    },
    {
        'code':        'ACCUMULATED_OTHER_COMPREHENSIVE_INCOME_NOT_RECLASSIFIED',
        'name':        'Accumulated Other Comprehensive Income—Not Reclassified',
        'description': 'Cumulative OCI items that will not be reclassified to profit or loss in subsequent periods.'
    },
    {
        'code':        'ACCUMULATED_OTHER_COMPREHENSIVE_INCOME_RECLASSIFIED',
        'name':        'Accumulated Other Comprehensive Income—Reclassified',
        'description': 'Cumulative OCI items that may be reclassified to profit or loss when specific conditions are met.'
    },
    {
        'code':        'RESTRICTED_RESERVES_APPROPRIATED_FROM_PROFIT',
        'name':        'Restricted Reserves Appropriated from Profit',
        'description': 'Portions of profit set aside as statutory or voluntary reserves and not distributable as dividends.'
    },
    {
        'code':        'OTHER_EQUITY_INTERESTS',
        'name':        'Other Equity Interests',
        'description': 'Equity stakes held by non-owners or third parties, not classified as non-controlling interests.'
    },
    {
        'code':        'OTHER_RESERVES',
        'name':        'Other Reserves',
        'description': 'Equity reserves not separately classified, including statutory and discretionary reserves.'
    },
    {
        'code':        'DIVIDEND_ADVANCES_PAID_NET',
        'name':        'Dividend Advances Paid (Net)',
        'description': 'Advances paid on dividends, net of any repayment or offsets.'
    },
    {
        'code':        'RETAINED_EARNINGS',
        'name':        'Retained Earnings',
        'description': 'Cumulative net profit or loss retained in the business, less dividends distributed.'
    },
    {
        'code':        'PROFIT_OR_LOSS_FOR_THE_PERIOD',
        'name':        'Profit or Loss for the Period',
        'description': 'Net result (profit or loss) recognized in the current reporting period.'
    },
    {
        'code':        'NON_CONTROLLING_INTERESTS',
        'name':        'Non-controlling Interests',
        'description': 'Equity in subsidiaries not attributable to the parent company’s shareholders.'
    },
    {
        'code':        'TOTAL_EQUITY',
        'name':        'Total Equity',
        'description': 'The residual interest in the assets of the entity after deducting liabilities.'
    },
    {
        'code':        'TOTAL_RESOURCES',
        'name':        'Total Resources',
        'description': 'The sum of total equity and total liabilities, representing all claims on the entity’s assets.'
    },
    {
        'code':        'NET_FOREIGN_CURRENCY_POSITION_INCLUDING_HEDGE',
        'name':        'Net Foreign Currency Position Including Hedge',
        'description': 'Net exposure to foreign currency risks, including the effect of hedging instruments.'
    },
    
]

SAMPLE_COMPANIES = [
    {'ticker':'KCHOL','name':'Koç Holding A.Ş.','aliases':'KCHOL, Koc Holding, Koç Holding A.Ş.','description':'Leading Turkish conglomerate with diversified holdings across industries.'},
    {'ticker':'SAHOL','name':'Sabancı Holding A.Ş.','aliases':'SAHOL, Sabanci Holding','description':'Major Turkish conglomerate active in finance, energy, and retail sectors.'},
    {'ticker':'THYAO','name':'Türk Hava Yolları A.Ş.','aliases':'THYAO, Turkish Airlines','description':'Flag carrier airline of Turkey, operating worldwide flights.'},    
    {'ticker':'TUPRS','name':'Türkiye Petrol Rafinerileri A.Ş.','aliases':'TUPRS, Tupras','description':'Turkey\'s largest oil refiner, producing fuel and petrochemical products.'},
    {'ticker':'TCELL','name':'Turkcell A.Ş.','aliases':'TCELL, Turkcell','description':'Leading mobile operator in Turkey offering telecommunications services.'},
    {'ticker':'TTKOM','name':'Türk Telekom A.Ş.','aliases':'TTKOM, Türk Telekom','description':'Integrated telecom operator providing fixed-line, mobile, and internet services.'},
    {'ticker':'SISE','name':'Türkiye Şişe ve Cam Fabrikaları A.Ş.','aliases':'SISE, Sisecam','description':'Global glass manufacturer with products in flat and glassware sectors.'},
    {'ticker':'TTRAK','name':'Türk Traktör ve Ziraat Makineleri A.Ş.','aliases':'TTRAK, Türk Traktör','description':'Leading tractor and agricultural machinery manufacturer in Turkey.'},
    {'ticker':'FROTO','name':'Ford Otomotiv Sanayi A.Ş.','aliases':'FROTO, Ford Otomotiv','description':'Automotive manufacturer and joint venture producing Ford-branded vehicles.'},
    {'ticker':'TOASO','name':'Tofaş Türk Otomobil Fabrikası A.Ş.','aliases':'TOASO, Tofaş','description':'Turkish automotive manufacturer producing Fiat-based passenger vehicles.'}
]