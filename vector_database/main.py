import os
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
import openai
from dotenv import load_dotenv
import numpy as np
from openai import OpenAI
from read_and_fill_facts import read_and_fill_facts, insert_total_liabilities
from create_hierarchy_map import update_parent_accounts
from agents import Agent, Runner, gen_trace_id, trace, function_tool, ModelSettings
from data import SAMPLE_ACCOUNTS, SAMPLE_COMPANIES
# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': 'database_trial',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'postgres',
    'port': '5432'
}

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)


# --- EMBEDDING UTILS ---
def get_embedding(text: str) -> list[float]:
    #print(text)
    resp = client.embeddings.create(model='text-embedding-ada-002', input=text)
    return resp.data[0].embedding

# --- NPY SAVE/LOAD ---
def save_embeddings(data: list[dict], id_field: str, filename: str):
    """Save ids, names, descriptions, embeddings to .npy files"""
    ids, names, descs, embs = [], [], [], []
    for item in data:
        ids.append(item[id_field])
        names.append(item['name'])
        descs.append(item['description'])
        txt = f"{item[id_field]} | {item['name']} | {item['description']}"
        embs.append(get_embedding(txt))
    arr = np.array(embs)
    base = os.path.join(DATA_DIR, filename)
    np.save(f"{base}_{id_field}s.npy", np.array(ids))
    np.save(f"{base}_names.npy", np.array(names))
    np.save(f"{base}_descs.npy", np.array(descs))
    np.save(f"{base}_embs.npy", arr)
    print(f"Saved {filename} embeddings.")


def load_embeddings(filename: str, id_field: str) -> list[dict]:
    """Load items with embeddings from .npy files"""
    base = os.path.join(DATA_DIR, filename)
    ids = np.load(f"{base}_{id_field}s.npy", allow_pickle=True)
    names = np.load(f"{base}_names.npy", allow_pickle=True)
    descs = np.load(f"{base}_descs.npy", allow_pickle=True)
    arr = np.load(f"{base}_embs.npy", allow_pickle=True)
    data = []
    for i in range(len(ids)):
        data.append({
            id_field: ids[i],
            'name': names[i],
            'description': descs[i],
            'embedding': arr[i].tolist()
        })
    return data

# --- DB INSERTS ---
def insert_table(data: list[dict], table: str, id_field: str, cols: list[str]):
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    vals = []
    for item in data:
        vec = '[' + ','.join(map(str, item['embedding'])) + ']'
        row = [item[id_field], item['name'], item['description'], vec]
        vals.append(tuple(row))
    cols_list = ', '.join(cols)
    sql = f"INSERT INTO {table} ({cols_list}) VALUES %s"
    execute_values(cur, sql, vals)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(vals)} rows into {table}.")

# --- INDEX & SEARCH HELPERS ---
def create_hnsw(table: str, column: str = 'embedding', m: int = 16, ef_con: int = 256):
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute(f"DROP INDEX IF EXISTS {table}_{column}_hnsw_idx;")
    cur.execute(
        f"CREATE INDEX IF NOT EXISTS {table}_{column}_hnsw_idx ON {table} USING hnsw ({column} vector_cosine_ops) WITH (m={m}, ef_construction={ef_con});"
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Created HNSW index on {table}.{column}.")


def search_hnsw(table: str, query: str, id_field: str, ef_search: int = 200, limit: int = 5):
    vec = get_embedding(query)
    vec_lit = '[' + ','.join(map(str, vec)) + ']'
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SET vector.hnsw.ef_search = %s;", (ef_search,))
    cur.execute(
        f"SELECT {id_field}, name FROM {table} ORDER BY embedding <=> %s::vector LIMIT {limit};",
        (vec_lit,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    print(f"\n[{table}] Top {limit} for '{query}':")
    for r in rows:
        print(f" - {r[0]}: {r[1]}")

def fill_periods_table():
    """
    Populate `period` with entries from Q1 2006 up through Q1 2025,
    inserting only (quarter, year).
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    # 1) Build list of (quarter, year) tuples
    records = []
    for year in range(2006, 2026):
        # stop at Q1 for 2025
        max_q = 1 if year == 2025 else 4
        for quarter in range(1, max_q + 1):
            records.append((quarter, year))

    # 2) Bulk‐insert into period; assume you've added a UNIQUE(year, quarter) constraint
    print(records)
    print(len(records))
    sql = """
        INSERT INTO period (quarter, year)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    execute_values(cur, sql, records)

    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted up to {len(records)} period rows (duplicates skipped).")


def _search_hnsw(table: str,
                 select_cols: list[str],
                 query: str,
                 ef_search: int = 200,
                 limit: int = 5) -> list[dict]:
    vec = get_embedding(query)
    vec_lit = "[" + ",".join(map(str, vec)) + "]"

    with psycopg2.connect(**DB_PARAMS) as conn, \
         conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SET vector.hnsw.ef_search = %s;", (ef_search,))
        cols = ", ".join(select_cols)
        cur.execute(
            f"SELECT {cols} FROM {table} "
            f"ORDER BY embedding <=> %s::vector LIMIT %s;",
            (vec_lit, limit)
        )
        return cur.fetchall()
def search_accounts_with_children(
    query: str,
    ef_search: int = 200,
    limit: int = 5
) -> list[dict]:
    """
    1) Find up to `limit` accounts most similar to `query` via HNSW on embeddings.
    2) For each matched account fetch all direct children.
    Returns a list of dicts with keys:
      - code, name, description, parent_code
      - children: list of dicts with keys code, name, description, parent_code
    """
    # embed the query
    vec = get_embedding(query)
    vec_lit = "[" + ",".join(map(str, vec)) + "]"

    with psycopg2.connect(**DB_PARAMS) as conn, \
         conn.cursor(cursor_factory=RealDictCursor) as cur:

        # set search effort
        cur.execute("SET vector.hnsw.ef_search = %s;", (ef_search,))

        # 1) fetch top-N matches, including parent code
        cur.execute(
            """
            SELECT
              a.account_id,
              a.code,
              a.name,
              a.description,
              p.code AS parent_code
            FROM account a
            LEFT JOIN account p
              ON a.parent_account_id = p.account_id
            ORDER BY a.embedding <=> %s::vector
            LIMIT %s;
            """,
            (vec_lit, limit)
        )
        matches = cur.fetchall()
        matched_ids = [r['account_id'] for r in matches]
        if not matched_ids:
            return []

        # 2) fetch all direct children of those matches
        cur.execute(
            """
            SELECT
              a.account_id,
              a.code,
              a.name,
              a.description,
              p.code AS parent_code
            FROM account a
            LEFT JOIN account p
              ON a.parent_account_id = p.account_id
            WHERE a.parent_account_id = ANY(%s);
            """,
            (matched_ids,)
        )
        children = cur.fetchall()

    # group children by their parent_code
    children_by_parent: dict[str, list[dict]] = {}
    for child in children:
        parent_code = child['parent_code']
        children_by_parent.setdefault(parent_code, []).append({
            'code':         child['code'],
            'name':         child['name'],
            'description':  child['description'],
            'parent_code':  child['parent_code']
        })

    # build final result, dropping numeric IDs
    result: list[dict] = []
    for acct in matches:
        result.append({
            'code':         acct['code'],
            'name':         acct['name'],
            'description':  acct['description'],
            'parent_code':  acct['parent_code'],
            'children':     children_by_parent.get(acct['code'], [])
        })

    return result
@function_tool
def get_similar_companies(company_name_prompt: str) -> list[dict]:
    """
    Get similar companies based on the given company name prompt.
    It will query the company table with embedding vector search and return the top 5 results.

    Args:
        company_name_prompt: Company name or ticker of the company to search for.
    Returns:
        A list of similar companies with their ticker, name, and description.
    """
    return _search_hnsw(table="company", select_cols=["ticker", "name", "description"], query=company_name_prompt, limit=5)

@function_tool
def get_similar_accounts(account_query_prompt: str) -> list[dict]:
    """
    Get similar accounts based on the given account query prompt. 
    It will query the account table with embedding vector search and return the top 5 results.
    If the account is a parent account, it will also return the children accounts.

    Args:
        account_query_prompt: Account query prompt.
    Returns:
        A list of similar accounts with their code, name, and description. If the account is a parent account, it will also return the children accounts.
    """
    return search_accounts_with_children(account_query_prompt)
    #return _search_hnsw( table="account", select_cols=["account_id", "code", "name", "description"], query=account_query_prompt,limit=5)

@function_tool
def query_with_sql(sql_query: str) -> list[dict]:
    """
    Query the database with the given SQL query. 
    It will return the results of the query.

    Args:
        sql_query: SQL query to execute.
    Returns:
        A list of results from the query.   
    """
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute(sql_query)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

# --- MAIN FLOW ---
async def main():
    # 1) Save embeddings for accounts & companies
    #save_embeddings(SAMPLE_ACCOUNTS, 'code', 'account')
    #save_embeddings(SAMPLE_COMPANIES, 'ticker', 'company')

    # 2) Insert into DB
    insert_table(load_embeddings('account', 'code'), 'account', 'code', ['code', 'name', 'description', 'embedding'])
    insert_table(load_embeddings('company', 'ticker'), 'company', 'ticker', ['ticker', 'name', 'description', 'embedding'])

    update_parent_accounts()

    fill_periods_table()

    read_and_fill_facts()

    insert_total_liabilities()

    # 3) Create HNSW indexes
    create_hnsw('account')
    create_hnsw('company')

    agent = Agent(
        name="Financial Statements Agent",
        instructions="You are a helpful professional financial analyst with expertise in financial statements and sql queries."
            "You will use the following tools to answer the user's question:"
            "1. get_similar_companies"
            "2. get_similar_accounts"
            "3. query_with_sql"
            "Before you use query_with_sql, If you need to get correct company or acounts table information, you can use get_similar_companies or get_similar_accounts tools."
            "Account can have children accounts. Parent account is the total of all its children accounts. if you need to get the total of all accounts, you should use the parent account."
            "Database Structure:\n"
            "account (account_id SERIAL PRIMARY KEY,code TEXT NOT NULL UNIQUE, parent_account_id  INTEGER NULL REFERENCES account(account_id) ON DELETE CASCADE,name TEXT NOT NULL UNIQUE,description TEXT NOT NULL)\n"
            "company (company_id SERIAL PRIMARY KEY,ticker TEXT NOT NULL UNIQUE,name TEXT NOT NULL UNIQUE,description TEXT NOT NULL)\n"            
            "period ( period_id   SERIAL PRIMARY KEY, quarter INTEGER NOT NULL,year INTEGER NOT NULL, CONSTRAINT uq_period_year_quarter UNIQUE (year, quarter))\n"
            "financial_fact (fact_id SERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES company(company_id) ON DELETE CASCADE,period_id INTEGER NOT NULL REFERENCES period(period_id) ON DELETE CASCADE, account_id INTEGER NOT NULLREFERENCES account(account_id) ON DELETE CASCADE, value NUMERIC(18,2) NOT NULL)\n"
            "You you query the dabase if you need to get account and/or company information. You must use get_similar_companies or get_similar_accounts tools to get the correct company or account information.\n"
            "Some of the accounts are subcategories of other accounts. If you need to get the total of all accounts, you should use the parent account. If you need to get the subcategories of an account, you should use the account itself.\n"
            "You don't need to sum up the values of the accounts. You can use the account itself to get the total value. If you need to get the total value of a category, you should use the parent account.\n"
            "For example TOTAL_LIABILITIES is the sum of TOTAL_SHORT_TERM_LIABILITIES and TOTAL_LONG_TERM_LIABILITIES. So if you need to get the total liabilities, you should use TOTAL_LIABILITIES not to sum up TOTAL_SHORT_TERM_LIABILITIES and TOTAL_LONG_TERM_LIABILITIES.\n",
        model="gpt-4o-mini",
        #model_settings=ModelSettings(temperature=0.2),
        tools=[get_similar_companies, get_similar_accounts, query_with_sql]
    )

    #result = await Runner.run(agent, input="Koc Holdingin Toplam Kısa Vadeli Yükümlülükleri hangi yıl hangi çeyrekte en azdır.")
    #print(result.final_output)
    test_messages = [
        # 1) En düşük varlıklar        
        #"What is the total value of Koç Holding's Current Assets in the fourth quarter of 2024?",
        #"What are the total items in Koç Holding's Current Assets category in the fourth quarter of 2024? Give me detailed breakdown of the accounts. Give me all the accounts of subcategories of Current Assets. Also give me all subcategories values of Current Assets.",

        "Koç holding 2024 yilinin 4 çeyreğinde bilançosu ile ilgili detaylı finansal rapor verir misin?",
        #"2024 yılının dördüncü çeyreğinde Koç Holdingin Dönen Varlıklar kategorisindeki toplam kalemler (account) hangileridir?",
        # #"Dönen Varlıklar kategorisindeki toplam kalemler (account) hangileridir?",        
        # "2024 yılının dördüncü çeyreğinde Koç Holdingin Other Current Assets detayli kalem kalem listele.",
        # # 2) En yüksek kısa vadeli yükümlülükler
        # "2022 yılının üçüncü çeyreğinde Toplam Kısa Vadeli Yükümlülükleri en yüksek 3 şirket hangileridir?",
        # # 3) Net gelir sıralaması
        # "2024 ikinci çeyrekte Toplam Uzun Vadeli Yükümlülükleri en fazla olan 3 şirketi sıralar mısın?",
        # # 4) Özsermaye değişimi
        # "Son üç çeyrekte  ŞişeCam'nin Toplam Özkaynakları nasıl değişti?",
        # # 5) Duran varlıklar
        # "2021 dördüncü çeyreğinde Toplam Duran Varlıkları en yüksek olan 5 şirket hangileridir?",
        # # 6) Kar karşılaştırması
        # "Sabancı Holding (SAHOL) ile Koç Holding (KCHOL) arasında 2023 üçüncü çeyrekte Toplam Kısa Vadeli Yükümlülükleri karşılaştırması yap.",
        # # 7) Kaynaklar sıralaması
        # "2020 yılının birinci çeyreğinde Toplam Varlıkları en fazla olan şirket hangisidir?",
        # # 8) Yükümlülük değişimi
        # "2024 birinci çeyrekte Toplam Yükümlülükleri en fazla azalan şirket hangisidir?",
        # # 9)  Trend analizi
        # "2022–2024 yılları arasında Tofaş'ın (TOASO) Toplam Duran Varlıkları yıllık bazda nasıl gelişti?",
        # # 10) Çeyreklik kıyaslama
        # "2023 ikinci çeyrek verilerine göre özkaynakları en büyük olan 5 şirketi listele."
    ]

    for msg in test_messages:
        print(f"Running: {msg}")
        result = await Runner.run(starting_agent=agent, input=msg)
        print(result.final_output)

    # 4) Test searches
    # Account queries
    # account_queries = [
    #     "What is the total assets of the company?",
    #     "What is the total liabilities of the company?",
    #     "What is the total equity of the company?",
    #     "What is the total resources of the company?"
    # ]
    #     "What is the total current assets of the company?",
    #     "What is the total fixed assets of the company?",
    #     "What is the total short-term liabilities of the company?",
    #     "What is the total long-term liabilities of the company?",
    #     # English paraphrases
    #     "How much are the company's current liabilities?",
    #     "Define total equity for this company.",
    #     # Turkish queries
    #     "Toplam varlıklarınızın ne olduğunu merak ediyorum.",
    #     "Toplam borçlarınızın ne olduğunu merak ediyorum.",
    #     "Toplam özkaynaklarınızın ne olduğunu merak ediyorum.",
    #     "Toplam kaynaklarınızın ne olduğunu merak ediyorum.",
    #     "Toplam dönen varlıklarınızın ne olduğunu merak ediyorum.",
    #     "Toplam duran varlıklarınızın ne olduğunu merak ediyorum."
    # ]

    # # Company queries
    # company_queries = [
    #     "Get details for Koç Holding.",
    #     "What does KCHOL stand for?",
    #     "Tell me about Türk Telekom.",
    #     "What is TTRAK's business?",
    #     "Give me info on SISE.",
    #     "Who is the parent company of Tofaş?",
    #     "Describe Türk Hava Yolları A.Ş.",
    #     "What products does Ford Otomotiv produce?",
    #     # English paraphrases
    #     "Provide a summary of Sabancı Holding.",
    #     "Sector information for Turkcell.",
    #     # Turkish queries
    #     "KCHOL hakkında bilgi ver.",
    #     "Sabancı Holding ne iş yapar?",
    #     "Türk Hava Yolları hakkında bilgi verir misin?",
    #     "TUPRS nedir?",
    #     "Türk Telekom hakkında ne biliyorsun?",
    #     "SISE şirketinin faaliyeti nedir?",
    #     "Tofaş nedir?"
    # ]

    # Run account searches
    # for q in account_queries:
    #     print(f"Running: {q}")
    #     results = search_accounts_with_children(q)
    #     print(results)
    
    # for q in account_queries:
    #     search_hnsw('account', q, 'code')

    # # Run company searches
    # for q in company_queries:
    #     search_hnsw('company', q, 'ticker')

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
