import os
import psycopg2
from psycopg2.extras import execute_values
import openai
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from openai import OpenAI

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': 'database_trial',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'postgres',  # Changed to use service name in Docker
    'port': '5432'
}

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Create data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Sample financial accounts
SAMPLE_ACCOUNTS = [
    {
        'code': 'TOTAL_ASSETS',
        'name': 'Total Assets',
        'description': 'The sum of all assets owned by the company, including current and fixed assets'
    },
    {
        'code': 'TOTAL_CURRENT_ASSETS',
        'name': 'Total Current Assets',
        'description': 'Assets that are expected to be converted to cash within one year, including cash, accounts receivable, and inventory'
    },
    {
        'code': 'TOTAL_FIXED_ASSETS',
        'name': 'Total Fixed Assets',
        'description': 'Long-term tangible assets used in operations (only fixed assets, excludes current assets), such as property, plant, and equipment'
    },
    {
        'code': 'TOTAL_RESOURCES',
        'name': 'Total Resources',
        'description': 'The total economic resources available to the company, including both assets and other resources'
    },
    {
        'code': 'TOTAL_LIABILITIES',
        'name': 'Total Liabilities',
        'description': 'The sum of all financial obligations and debts owed by the company'
    },
    {
        'code': 'TOTAL_LONG_TERM_LIABILITIES',
        'name': 'Total Long-term Liabilities',
        'description': 'Financial obligations that are due beyond one year, including long-term loans and bonds'
    },
    {
        'code': 'TOTAL_SHORT_TERM_LIABILITIES',
        'name': 'Total Short-term Liabilities',
        'description': 'Financial obligations that are due within one year, including accounts payable and short-term loans'
    },
    {
        'code': 'TOTAL_EQUITY',
        'name': 'Total Equity',
        'description': 'The residual interest in the assets of the company after deducting liabilities, representing ownership interest'
    }
]

SAMPLE_COMPANIES = [
    {
        'ticker': 'KCHOL',
        'name': 'Koç Holding A.Ş.',
        'allias': 'KCHOL, Koc Holding, Koç Holding, Koç Holding A.Ş.',
        'description': 'Koç Holding A.Ş. is a holding company that owns a majority stake in many companies in Turkey.'
    },
    {
        'ticker': 'SAHOL',
        'name': 'Sahol Holding A.Ş.',
        'allias': 'SAHOL, Sahol Holding, Sahol Holding A.Ş.',
        'description': 'Sahol Holding A.Ş. is a holding company that owns a majority stake in many companies in Turkey.'
    },
    {
        'ticker': 'THYAO',
        'name': 'Türk Hava Yolları A.Ş.',
        'allias': 'THYAO, Türk Hava Yolları, Türk Hava Yolları A.Ş.',
        'description': 'Türk Hava Yolları A.Ş. is a holding company that owns a majority stake in many companies in Turkey.'
    },
    {
        'ticker': 'TUPRS',
        'name': 'Türkiye Petrol Rafinerileri A.Ş.',
        'allias': 'TUPRS, Türkiye Petrol Rafinerileri, Türkiye Petrol Rafinerileri A.Ş.',
        'description': 'Türkiye Petrol Rafinerileri A.Ş. is a holding company that owns a majority stake in many companies in Turkey.'
    },
    {
        'ticker': 'TCELL',
        'name': 'Turkcell A.Ş.',
        'allias': 'TCELL, Turkcell, Turkcell A.Ş.',
        'description': 'Turkcell A.Ş. is a holding company that owns a majority stake in many companies in Turkey.'
    },
    {   
        'ticker': 'TTKOM',
        'name': 'Türk Telekom A.Ş.',
        'allias': 'TTKOM, Türk Telekom, Türk Telekom A.Ş.',
        'description': 'Türk Telekom A.Ş. is a holding company that owns a majority stake in many companies in Turkey.'
    },
    {
        'ticker': 'SISE',
        'name': 'Türkiye Şişe ve Cam Fabrikaları A.Ş.',
        'allias': 'SISE, Türkiye Şişe ve Cam Fabrikaları, Türkiye Şişe ve Cam Fabrikaları A.Ş.',
        'description': 'Türkiye Şişe ve Cam Fabrikaları A.Ş. is a holding company that owns a majority stake in many companies in Turkey.'
    },
    {
        'ticker': 'TTRAK',
        'name': 'Türk Traktör ve Ziraat Makineleri A.Ş.',
        'allias': 'TTRAK, Türk Traktör, Türk Traktör ve Ziraat Makineleri, Türk Traktör ve Ziraat Makineleri A.Ş.',
        'description': 'Türk Traktör ve Ziraat Makineleri A.Ş. is a holding company that owns a majority stake in many companies in Turkey.'
    },
    {
        'ticker': 'FROTO',
        'name': 'Ford Otomotiv Sanayi A.Ş.',
        'allias': 'FROTO, Ford Otomotiv, Ford Otomotiv Sanayi A.Ş.',
        'description': 'Ford Otomotiv Sanayi A.Ş. is a holding company that owns a majority stake in many companies in Turkey.'
    },
    {
        'ticker': 'TOASO',
        'name': 'Tofaş Türk Otomobil Fabrikası A.Ş.',
        'allias': 'TOASO, Tofaş, Tofaş Türk Otomobil Fabrikası A.Ş.',
        'description': 'Tofaş Türk Otomobil Fabrikası A.Ş. is a holding company that owns a majority stake in many companies in Turkey.'
    }    
]

def get_embedding(text):
    """Get embedding for a given text using OpenAI's API"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
        encoding_format="float"
    )
    return response.data[0].embedding

def save_embeddings_to_npy(accounts, filename='account_embeddings.npy'):
    """Save account data and embeddings to numpy files"""
    # Create arrays to store all data
    codes = []
    names = []
    descriptions = []
    embeddings = []

    turkish = {
        'TOTAL_ASSETS': 'Toplam Varlıklar',
        'TOTAL_CURRENT_ASSETS': 'Dönen Varlıklar',
        'TOTAL_FIXED_ASSETS': 'Duran Varlıklar',
        'TOTAL_RESOURCES': 'Toplam Kaynaklar',
        'TOTAL_LIABILITIES': 'Toplam Yükümlülükler',
        'TOTAL_LONG_TERM_LIABILITIES': 'Uzun Vadeli Yükümlülükler',
        'TOTAL_SHORT_TERM_LIABILITIES': 'Kısa Vadeli Yükümlülükler',
        'TOTAL_EQUITY': 'Toplam Özkaynak'
    }
    
    for account in accounts:
        # Get embedding for the combined text
        combined_text = (
            f"{account['code']} | "
            f"{account['name']} | "
            f"{account['description']}"
        )

        # determine category/subcategory
        cat = "Asset" if "ASSETS" in account['code'] else "Liability" if "LIABILITIES" in account['code'] else "Equity"
        subcat = ("Current" if "CURRENT" in account['code']
                  else "Fixed" if "FIXED" in account['code']
                  else "Long-Term" if "LONG_TERM" in account['code']
                  else "Short-Term" if "SHORT_TERM" in account['code']
                  else "All")

        combined_text = " | ".join([
            account['code'],
            account['name'],
            account['description'],
            f"Category: {cat}",
            f"Subcategory: {subcat}",
            f"Turkish: {turkish.get(account['code'], '')}"
        ])
        embedding = get_embedding(combined_text)
        
        # Store the data
        codes.append(account['code'])
        names.append(account['name'])
        descriptions.append(account['description'])
        embeddings.append(embedding)
    
    # Convert to numpy arrays
    codes = np.array(codes)
    names = np.array(names)
    descriptions = np.array(descriptions)
    embeddings = np.array(embeddings)
    
    # Save to files
    base_path = os.path.join(DATA_DIR, os.path.splitext(filename)[0])
    np.save(f"{base_path}_codes.npy", codes)
    np.save(f"{base_path}_names.npy", names)
    np.save(f"{base_path}_descriptions.npy", descriptions)
    np.save(f"{base_path}_embeddings.npy", embeddings)
    
    print(f"Accounts embeddings saved to {base_path}_*.npy files")

    # Save companies embeddings

def load_embeddings_from_npy(filename='account_embeddings.npy'):
    """Load account data and embeddings from numpy files"""
    base_path = os.path.join(DATA_DIR, os.path.splitext(filename)[0])
    
    try:
        # Load the numpy arrays
        codes = np.load(f"{base_path}_codes.npy")
        names = np.load(f"{base_path}_names.npy")
        descriptions = np.load(f"{base_path}_descriptions.npy")
        embeddings = np.load(f"{base_path}_embeddings.npy")
        
        # Convert to list of dictionaries
        accounts = []
        for i in range(len(codes)):
            accounts.append({
                'code': codes[i],
                'name': names[i],
                'description': descriptions[i],
                'embedding': embeddings[i].tolist()
            })
        return accounts
    except FileNotFoundError:
        print(f"Files not found in {base_path}")
        return None

def insert_account_from_npy(filename='account_embeddings.npy'):
    """Insert accounts from numpy files into the database"""
    accounts = load_embeddings_from_npy(filename)
    if not accounts:
        return
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        for account in accounts:
            # Convert the embedding list to a PostgreSQL vector
            embedding_vector = f"[{','.join(map(str, account['embedding']))}]"
            cur.execute(
                """
                INSERT INTO account (code, name, description, embedding)
                VALUES (%s, %s, %s, %s::vector)
                """,
                (account['code'], account['name'], account['description'], embedding_vector)
            )
        conn.commit()
        print(f"Successfully inserted {len(accounts)} accounts from {filename}")
    except Exception as e:
        print(f"Error inserting accounts: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def train_ivfflat_index():
    """Retrain the IVFFlat index so centroids reflect all rows"""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        cur.execute("REINDEX INDEX CONCURRENTLY account_embedding_ivfflat_idx;")
        conn.commit()
        print("Index retrained successfully.")
    except Exception as e:
        print(f"Error retraining index: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def test_similarity_search_ivfflat(query_text, probes=10):
    """Test similarity using IVFFlat (approximate)"""
    query_embedding = get_embedding(query_text)
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        # Set number of IVF probes for this session
        cur.execute("SET ivfflat.probes = %s;", (probes,))
        # Convert to vector literal
        query_vector = '[' + ','.join(map(str, query_embedding)) + ']'
        cur.execute(
            """
            SELECT code, name
              FROM account
             ORDER BY embedding <=> %s::vector
             LIMIT 5
            """,
            (query_vector,)
        )
        results = cur.fetchall()
        print(f"\n[IVFFlat] Similar accounts for '{query_text}' (probes={probes}):")
        for code, name in results:
            print(f"  - {code}: {name}")
    except Exception as e:
        print(f"Error performing IVFFlat search: {e}")
    finally:
        cur.close()
        conn.close()

def test_similarity_search_hnsw(query_text, ef_search=200):
    """Test similarity using HNSW (near-exact)"""
    query_embedding = get_embedding(query_text)
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        # Set HNSW search breadth for this session
        cur.execute("SET vector.hnsw.ef_search = %s;", (ef_search,))
        # Convert to vector literal
        query_vector = '[' + ','.join(map(str, query_embedding)) + ']'
        cur.execute(
            """
            SELECT code, name
              FROM account
             ORDER BY embedding <=> %s::vector
             LIMIT 5
            """,
            (query_vector,)
        )
        results = cur.fetchall()
        print(f"\n[HNSW] Similar accounts for '{query_text}' (ef_search={ef_search}):")
        for code, name in results:
            print(f"  - {code}: {name}")
    except Exception as e:
        print(f"Error performing HNSW search: {e}")
    finally:
        cur.close()
        conn.close()
def main():
    # Save embeddings to numpy files
    save_embeddings_to_npy(SAMPLE_ACCOUNTS)
    
    # Insert accounts from numpy files
    insert_account_from_npy()
    # Retrain the IVFFlat index
    #train_ivfflat_index()
    
    # Test the similarity search
    test_queries = [
        "What is the total assets of the company?",
        "What is the total liabilities of the company?",
        "What is the total equity of the company?",
        "What is the total resources of the company?",
        "What is the total current assets of the company?",
        "What is the total fixed assets of the company?",
        "What is the total short-term liabilities of the company?",
        "What is the total long-term liabilities of the company?",
        # Turkish queries
        "Toplam varlıklarınızın ne olduğunu merak ediyorum.",
        "Toplam borçlarınızın ne olduğunu merak ediyorum.",
        "Toplam özkaynaklarınızın ne olduğunu merak ediyorum.",
        "Toplam kaynaklarınızın ne olduğunu merak ediyorum.",
        "Toplam dönen varlıklarınızın ne olduğunu merak ediyorum.",
        "Toplam duran varlıklarınızın ne olduğunu merak ediyorum."
    ]
    
    for query in test_queries:
        test_similarity_search_hnsw(query,ef_search=20)

if __name__ == "__main__":
    main() 