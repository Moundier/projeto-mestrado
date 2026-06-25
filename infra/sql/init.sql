-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Audit log table (immutable, append-only)
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id VARCHAR(100) NOT NULL,
    tool_name VARCHAR(50) NOT NULL,
    input_summary TEXT,
    output_reference TEXT,
    checksum VARCHAR(64)
);

-- Index for audit queries
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log (user_id);

-- CBR cases table (for persistent storage)
CREATE TABLE IF NOT EXISTS cbr_cases (
    id SERIAL PRIMARY KEY,
    case_uuid UUID DEFAULT gen_random_uuid(),
    product_type VARCHAR(200),
    destination_country VARCHAR(100),
    export_quantity_kg FLOAT,
    raw_material_kg FLOAT,
    species TEXT[],
    suppliers TEXT[],
    invoice_count INT,
    company_cnpj VARCHAR(20),
    company_rgp VARCHAR(50),
    outcome VARCHAR(50),
    approval_days INT,
    created_at TIMESTAMP DEFAULT NOW()
);
