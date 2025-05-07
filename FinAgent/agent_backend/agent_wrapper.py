import os
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
import openai
from dotenv import load_dotenv
import numpy as np
from openai import OpenAI
from read_and_fill_facts import read_and_fill_facts
from agents import Agent, Runner, gen_trace_id, trace, function_tool
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

@function_tool
def get_similar_companies(company_name_prompt: str) -> list[dict]:
    """
    Get similar companies based on the given company name prompt.
    It will query the company table with embedding vector search and return the top 5 results.

    Args:
        company_name_prompt: Company name or ticker of the company to search for.
    Returns:
        A list of similar companies with their company_id, ticker, name, and description.
    """
    return _search_hnsw(table="company", select_cols=["company_id", "ticker", "name", "description"], query=company_name_prompt, limit=5)

@function_tool
def get_similar_accounts(account_query_prompt: str) -> list[dict]:
    """
    Get similar accounts based on the given account query prompt. 
    It will query the account table with embedding vector search and return the top 5 results.

    Args:
        account_query_prompt: Account query prompt.
    Returns:
        A list of similar accounts with their account_id, code, name, and description.
    """
    return _search_hnsw( table="account", select_cols=["account_id", "code", "name", "description"], query=account_query_prompt,limit=5)

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

def initialize_agent():
    insert_table(load_embeddings('account', 'code'), 'account', 'code', ['code', 'name', 'description', 'embedding'])
    insert_table(load_embeddings('company', 'ticker'), 'company', 'ticker', ['ticker', 'name', 'description', 'embedding'])

    fill_periods_table()

    read_and_fill_facts()

    # 3) Create HNSW indexes
    create_hnsw('account')
    create_hnsw('company')

    return Agent(
        name="Financial Statements Agent",
        instructions="You are a helpful professional financial analyst with expertise in financial statements and sql queries."
            "You will use the following tools to answer the user's question:"
            "1. get_similar_companies"
            "2. get_similar_accounts"
            "3. query_with_sql"
            "Before you use query_with_sql, If you need to get correct company or acounts table information, you can use get_similar_companies or get_similar_accounts tools."
            "Database Structure:\n"
            "account (account_id SERIAL PRIMARY KEY,code TEXT NOT NULL UNIQUE,name TEXT NOT NULL UNIQUE,description TEXT NOT NULL)\n"
            "company (company_id SERIAL PRIMARY KEY,ticker TEXT NOT NULL UNIQUE,name TEXT NOT NULL UNIQUE,description TEXT NOT NULL)\n"            
            "period ( period_id   SERIAL PRIMARY KEY, quarter INTEGER NOT NULL,year INTEGER NOT NULL, CONSTRAINT uq_period_year_quarter UNIQUE (year, quarter))\n"
            "financial_fact (fact_id SERIAL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES company(company_id) ON DELETE CASCADE,period_id INTEGER NOT NULL REFERENCES period(period_id) ON DELETE CASCADE, account_id INTEGER NOT NULLREFERENCES account(account_id) ON DELETE CASCADE, value NUMERIC(18,2) NOT NULL)\n"
            "You you query the dabase if you need to get account and/or company information. You must use get_similar_companies or get_similar_accounts tools to get the correct company or account information.",
        model="gpt-4o-mini",
        tools=[get_similar_companies, get_similar_accounts, query_with_sql]
    )

# Initialize agent only when needed
agent = None

async def send_message(message: str):
    global agent
    if agent is None:
        agent = initialize_agent()
    result = await Runner.run(agent, input=message)
    return result.final_output

    