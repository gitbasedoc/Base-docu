-- Migration: Ajout du compteur de vues aux procédures
-- Date: 2025-12-18
-- Description: Ajoute la colonne views_count pour tracker les vues sur les procédures

-- Ajouter la colonne views_count
ALTER TABLE procedures ADD COLUMN IF NOT EXISTS views_count INTEGER DEFAULT 0;

-- Initialiser à 0 pour les procédures existantes
UPDATE procedures SET views_count = 0 WHERE views_count IS NULL;

-- Vérification
SELECT COUNT(*) as procedures_updated FROM procedures WHERE views_count IS NOT NULL;
