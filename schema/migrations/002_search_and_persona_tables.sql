-- Migration 002: Search and Persona Tables
-- Creates tables for search queries and user personas

CREATE TABLE IF NOT EXISTS search_queries (
    search_query_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    query_text VARCHAR(500) NOT NULL,
    search_type VARCHAR(50) NOT NULL CHECK (search_type IN ('doctor', 'service', 'specialty', 'package')),
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS personas (
    persona_id SERIAL PRIMARY KEY,
    persona_name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    characteristics TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_personas (
    user_persona_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    persona_id INTEGER NOT NULL,
    confidence_score DECIMAL(3, 2),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (persona_id) REFERENCES personas(persona_id) ON DELETE CASCADE,
    UNIQUE(user_id, persona_id)
);

CREATE INDEX idx_search_queries_user ON search_queries(user_id);
CREATE INDEX idx_search_queries_type ON search_queries(search_type);
CREATE INDEX idx_search_queries_created ON search_queries(created_at);
CREATE INDEX idx_user_personas_user ON user_personas(user_id);
CREATE INDEX idx_user_personas_persona ON user_personas(persona_id);