-- Create the documents table with the required structure for SupabaseVectorStore
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    metadata JSONB,
    embedding VECTOR(1536)
);

-- Create an index on the embedding column for faster similarity search
CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Enable RLS (Row Level Security)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (you can modify this based on your security requirements)
CREATE POLICY "Allow all operations" ON documents
    FOR ALL
    USING (true)
    WITH CHECK (true); 