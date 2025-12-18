-- Migration: Création de la table des favoris
-- Date: 2025-12-18
-- Description: Permet aux utilisateurs de bookmarker leurs procédures préférées

-- Créer la table favorites
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    procedure_id INTEGER NOT NULL REFERENCES procedures(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Contrainte d'unicité: un utilisateur ne peut mettre une procédure en favori qu'une fois
    CONSTRAINT unique_user_procedure_favorite UNIQUE (user_id, procedure_id)
);

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_procedure_id ON favorites(procedure_id);
CREATE INDEX IF NOT EXISTS idx_favorites_user_created ON favorites(user_id, created_at);

-- Vérification
SELECT
    COUNT(*) as total_favorites,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT procedure_id) as unique_procedures
FROM favorites;
