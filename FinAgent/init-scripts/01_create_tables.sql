-- 1) Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2) Create the account table
CREATE TABLE IF NOT EXISTS account (
  account_id   SERIAL PRIMARY KEY,
  code         TEXT   NOT NULL UNIQUE,
  parent_account_id  INTEGER NULL REFERENCES account(account_id) ON DELETE CASCADE,
  name         TEXT   NOT NULL UNIQUE,
  description  TEXT   NOT NULL,
  embedding    vector(1536)
);

CREATE INDEX idx_account_parent 
  ON account(parent_account_id);

-- -- 3) Create a named IVFFlat index with 100 lists
-- CREATE INDEX IF NOT EXISTS account_embedding_ivfflat_idx
--   ON account
--   USING ivfflat (embedding vector_cosine_ops)
--   WITH (lists = 100);


-- Create an HNSW index (no manual training required)
CREATE INDEX IF NOT EXISTS account_embedding_hnsw_idx
  ON account
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 256);


CREATE TABLE IF NOT EXISTS company (
  company_id   SERIAL PRIMARY KEY,
  ticker         TEXT   NOT NULL UNIQUE,
  name         TEXT   NOT NULL UNIQUE,
  description  TEXT   NOT NULL,
  embedding    vector(1536)
);

CREATE INDEX IF NOT EXISTS company_embedding_hnsw_idx
  ON company
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 256);



CREATE TABLE IF NOT EXISTS period (
  period_id   SERIAL PRIMARY KEY,
  quarter     INTEGER NOT NULL,
  year        INTEGER NOT NULL,
  CONSTRAINT uq_period_year_quarter UNIQUE (year, quarter)
);



-- 1) Create the financial_fact table (allowing multiple facts per company/period/account)
CREATE TABLE IF NOT EXISTS financial_fact (
    fact_id       SERIAL       PRIMARY KEY,
    company_id    INTEGER      NOT NULL
                       REFERENCES company(company_id)
                       ON DELETE CASCADE,
    period_id     INTEGER      NOT NULL
                       REFERENCES period(period_id)
                       ON DELETE CASCADE,
    account_id    INTEGER      NOT NULL
                       REFERENCES account(account_id)
                       ON DELETE CASCADE,
    value         NUMERIC(18,2) NOT NULL
);

-- 2) Indexes on the foreign-key columns for faster joins
CREATE INDEX IF NOT EXISTS idx_fin_fact_company ON financial_fact(company_id);
CREATE INDEX IF NOT EXISTS idx_fin_fact_period  ON financial_fact(period_id);
CREATE INDEX IF NOT EXISTS idx_fin_fact_account ON financial_fact(account_id);
