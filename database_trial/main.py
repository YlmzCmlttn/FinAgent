import asyncio
import os
import shutil

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio
from read_create import read_create_tables


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Financial Statements Agent",
        instructions=
        "You are a helpful professional financial analyst with expertise in financial statements and sql queries."
        "Database Structure:\n"        
        "Tables in database:\n"
        "account, company, financial_fact, period, statement_type\n\n"
        "1. Company Table:\n"
        "   - company_id (PK): Unique identifier\n"
        "   - ticker: Company stock ticker (e.g., 'KCHOL')\n"
        "   - name: Full company name (e.g., 'Koç Holding A.Ş.')\n"
        "   - Relationships: Has many FinancialFacts\n\n"
        "2. StatementType Table:\n"
        "   - statement_type_id (PK): Unique identifier\n"
        "   - code: Statement code (e.g., 'BS')\n"
        "   - description: Statement description\n"
        "   - Relationships: Has many Accounts and Periods\n\n"
        "3. Account Table:\n"
        "   - account_id (PK): Unique identifier\n"
        "   - statement_type_id (FK): References StatementType\n"
        "   - code: Account code (e.g., 'CURRENT_ASSETS')\n"
        "   - name: Account name in Turkish (e.g., 'Dönen Varlıklar')\n"
        "   - Relationships: Belongs to StatementType, Has many FinancialFacts\n\n"
        "4. Period Table:\n"
        "   - period_id (PK): Unique identifier\n"
        "   - statement_type_id (FK): References StatementType\n"
        "   - frequency: 'Q' for Quarterly, 'A' for Annual\n"
        "   - year: Year of the period\n"
        "   - quarter: Quarter number (1-4)\n"
        "   - Relationships: Belongs to StatementType, Has many FinancialFacts\n\n"
        "5. FinancialFact Table:\n"
        "   - fact_id (PK): Unique identifier\n"
        "   - company_id (FK): References Company\n"
        "   - period_id (FK): References Period\n"
        "   - account_id (FK): References Account\n"
        "   - value: Numeric value of the fact\n"
        "   - Relationships: Belongs to Company, Period, and Account\n\n"
        "Key Relationships:\n"
        "- Company -> FinancialFact (One-to-Many)\n"
        "- StatementType -> Account (One-to-Many)\n"
        "- StatementType -> Period (One-to-Many)\n"
        "- Account -> FinancialFact (One-to-Many)\n"
        "- Period -> FinancialFact (One-to-Many)\n\n"
        "Tables in database:\n"
        "account, company, financial_fact, period, statement_type\n\n"
        "Common Account Names:\n"
        "- TOTAL_ASSETS\n"
        "- TOTAL_CURRENT_ASSETS\n"
        "- TOTAL_FIXED_ASSETS\n"
        "- TOTAL_RESOURCES\n"
        "- TOTAL_LIABILITIES\n"
        "- TOTAL_LONG_TERM_LIABILITIES\n"
        "- TOTAL_SHORT_TERM_LIABILITIES\n"
        "- TOTAL_EQUITY\n\n"
        "When retrieving data:\n"
        "1. First get all company names from the database then select the correct one with ticker.\n"
        "2. For account names, get all account names from the database then select the correct one with account code.\n"
        "3. For statement codes, get all statement codes from the database then select the correct one with statement description.\n"
        "4. For periods, get all periods from the database then select the correct one with year and quarter.\n"
        "5. Finally, get financial facts from the database then select the correct one with company id, account id and period id. Very important: If asked different account names then it not in the database, get all account names and codesfrom the database then use the most relevant one. If question has to need to know year and if it is not specified, then ask to user to specify the year. If question has not specified account name, then get the most relevant one. If question has not specified statement code, then get the most relevant one. If question has to need to know period and if it is not specified, then ask to user to specify the period. If question has to need to know company and if it is not specified, then ask to user to specify the company. SQL Query must return every detaild of the question to dobule check like company name, account name, statement code, period, year, quarter.\n"
        "SQL Query must return every detaild of the question to dobule check like company name, account name, statement code, period, year, quarter.\n"
        "DO NOT SHARE SQL QUERY WITH USER, ONLY RETURN THE RESULT OF THE QUERY.\n"
        "Very Important: This is a POSTGRES DATABASE, so you need to use the correct syntax for the database.\n",
        mcp_servers=[mcp_server],
        model="gpt-4o-mini"
    )

    # List the files it can read
    message = "KCHOL Toplam Kısa Vadeli Yükümlülükleri hangi yıl hangi çeyrekte en azdır."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # message = "Toplam borçları 2024 yılında 1. çeyrekte en az olan ve en çok olan şirketler hangisileridir?"
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)


    message = "Toplam Kısa Vadeli Yükümlülükleri en az olan şirket hangisidir?"
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # message = "2024 yilinin birinci çeyreğinde Toplam Özkaynakları en fazla olan 3 şirket hangisidir?"
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)


    # message = "Son 4 çeyrekte Toplam Varlıkları en hızlı büyüyen 3 şirketi bul ve bu şirketlerin her çeyrekteki Toplam Özkaynaklarındaki değişimi, Toplam Borçlarının Toplam Varlıklarına oranını (borç/varlık oranı) ve Toplam Dönen Varlıklarının Toplam Kısa Vadeli Yükümlülüklerine oranını (cari oran) göster."
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)

    # message = "2024 yılının birinci çeyreğinde, Toplam Dönen Varlıkları Toplam Kısa Vadeli Yükümlülüklerinden fazla olan, Toplam Özkaynakları son 4 çeyrekte artış gösteren ve Toplam Uzun Vadeli Yükümlülüklerinin Toplam Varlıklarına oranı %30'un altında olan şirketleri bul ve bu şirketlerin tüm finansal oranlarını göster."
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)

    # message = "2024 yılının birinci çeyreğinde, Toplam Kısa Vadeli Yükümlülüklerinin Toplam Dönen Varlıklarına oranı %50'nin üzerinde olan ve Toplam Uzun Vadeli Yükümlülükleri son 4 çeyrekte artış gösteren şirketleri bul ve bu şirketlerin her çeyrekteki Toplam Varlık, Toplam Borç ve Toplam Özkaynak değişimlerini göster."
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)


    # message = "Son 4 çeyrekte Toplam Varlıkları en hızlı büyüyen 3 şirketi bul ve bu şirketlerin her çeyrekteki Toplam Özkaynak büyüme oranlarını, Toplam Borçlarının Toplam Varlıklarına oranındaki değişimi ve Toplam Dönen Varlıklarının Toplam Varlıklarına oranındaki değişimi göster."
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)


    # message = "2024 yılının birinci çeyreğinde, Toplam Duran Varlıklarının Toplam Varlıklarına oranı %60'ın üzerinde olan şirketleri bul ve bu şirketlerin Toplam Özkaynaklarının Toplam Varlıklarına oranını, Toplam Uzun Vadeli Yükümlülüklerinin Toplam Borçlarına oranını ve son 4 çeyrekteki Toplam Varlık büyüme oranlarını göster."
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)


    # message = "Son 4 çeyrekte Toplam Özkaynakları artış gösteren, Toplam Dönen Varlıkları Toplam Kısa Vadeli Yükümlülüklerinden fazla olan ve Toplam Uzun Vadeli Yükümlülüklerinin Toplam Varlıklarına oranı %40'ın altında olan şirketleri bul ve bu şirketlerin her çeyrekteki tüm finansal oranlarını ve büyüme göstergelerini detaylı olarak göster."
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)


    # message = "2024 yılının birinci çeyreğinde, Toplam Dönen Varlıklarının Toplam Kısa Vadeli Yükümlülüklerine oranı 1.5'in üzerinde olan ve Toplam Duran Varlıklarının Toplam Uzun Vadeli Yükümlülüklerine oranı 2'nin üzerinde olan şirketleri bul ve bu şirketlerin son 4 çeyrekteki varlık-borç yapısındaki değişimleri göster."
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)





async def main():

    
    read_create_tables()    
    async with MCPServerStdio(
        name="Postgres Server, via npx",
        params={
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-postgres",
                "postgresql://postgres:postgres@postgres:5432/database_trial"
            ]
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP Filesystem Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it with `npm install -g npx`.")

    asyncio.run(main())
