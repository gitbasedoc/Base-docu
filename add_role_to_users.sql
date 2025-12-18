-- Migration: Ajout du champ role au modèle User
-- Date: 2025-12-18
-- Description: Ajoute un système de rôles (viewer, contributor, admin) pour remplacer is_admin

-- Ajout de la colonne role avec valeur par défaut
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'viewer' NOT NULL;

-- Création d'un index sur role pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Migration des utilisateurs existants : is_admin=true -> role='admin'
UPDATE users SET role = 'admin' WHERE is_admin = true AND role = 'viewer';

-- Migration des autres utilisateurs : définir comme 'contributor' par défaut pour les utilisateurs actifs existants
-- (ajustez cette logique selon vos besoins)
UPDATE users SET role = 'contributor' WHERE is_admin = false AND role = 'viewer' AND id IN (
    SELECT DISTINCT created_by FROM procedures WHERE created_by IS NOT NULL
);

-- Afficher le résultat de la migration
SELECT
    role,
    COUNT(*) as count
FROM users
GROUP BY role
ORDER BY role;
