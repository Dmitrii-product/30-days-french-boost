-- Supabase table setup for 30-days-french-boost
-- Run this in the Supabase SQL Editor (Dashboard > SQL Editor > New Query)

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id_hash TEXT PRIMARY KEY,
    encrypted_id TEXT NOT NULL,
    level TEXT NOT NULL DEFAULT 'C1',
    last_golden_list_at DATE DEFAULT '2026-04-08'
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 2. Vocabulary table
CREATE TABLE IF NOT EXISTS vocabulary (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_hash TEXT NOT NULL REFERENCES users(id_hash) ON DELETE CASCADE,
    word TEXT NOT NULL,
    is_learned BOOLEAN NOT NULL DEFAULT TRUE,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_hash, word)
);

ALTER TABLE vocabulary ENABLE ROW LEVEL SECURITY;
