-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    roll_number VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    face_embedding vector(512),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    roll_number VARCHAR(50),
    full_name VARCHAR(100),
    marked_at TIMESTAMP DEFAULT NOW(),
    confidence FLOAT,
    session_id VARCHAR(100)
);

-- Create index for faster similarity search
CREATE INDEX ON users USING ivfflat (face_embedding vector_cosine_ops) WITH (lists = 100);

-- Function for face similarity search
CREATE OR REPLACE FUNCTION match_faces(
    query_embedding vector(512),
    match_threshold float DEFAULT 0.6,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id int,
    roll_number varchar,
    full_name varchar,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.roll_number,
        u.full_name,
        1 - (u.face_embedding <=> query_embedding) as similarity
    FROM users u
    WHERE u.face_embedding IS NOT NULL
    AND 1 - (u.face_embedding <=> query_embedding) > match_threshold
    ORDER BY u.face_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;