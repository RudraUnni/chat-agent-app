-- Initial database setup for ChatApp
-- This script runs when the PostgreSQL container first starts

-- Create additional extensions that might be useful for a chat application
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For better JSONB indexing

-- Create a read-only user for analytics/reporting (optional)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'chatapp_readonly') THEN
        CREATE ROLE chatapp_readonly;
    END IF;
END
$$;

-- Grant connect permission
GRANT CONNECT ON DATABASE chatapp_db TO chatapp_readonly;

-- Note: Table-specific permissions will be granted after tables are created via migrations