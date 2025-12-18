-- Migration: Création de la table suggestions
-- Date: 2025-12-18
-- Description: Table pour gérer les suggestions d'amélioration de l'application par les utilisateurs

-- Création de la table suggestions
CREATE TABLE IF NOT EXISTS suggestions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,  -- feature, bug, improvement, other
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,  -- pending, reviewed, accepted, rejected, implemented
    admin_response TEXT,
    priority VARCHAR(20),  -- low, medium, high
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_suggestions_user_id ON suggestions(user_id);
CREATE INDEX IF NOT EXISTS idx_suggestions_category ON suggestions(category);
CREATE INDEX IF NOT EXISTS idx_suggestions_status ON suggestions(status);
CREATE INDEX IF NOT EXISTS idx_suggestions_created_at ON suggestions(created_at DESC);

-- Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_suggestions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_suggestions_updated_at ON suggestions;
CREATE TRIGGER trigger_suggestions_updated_at
    BEFORE UPDATE ON suggestions
    FOR EACH ROW
    EXECUTE FUNCTION update_suggestions_updated_at();

-- Vérification
SELECT
    COUNT(*) as total_suggestions,
    category,
    status
FROM suggestions
GROUP BY category, status;
