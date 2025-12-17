-- Ajouter la recherche plein texte PostgreSQL pour les procédures

-- 1. Ajouter la colonne search_vector de type TSVECTOR
ALTER TABLE procedures ADD COLUMN IF NOT EXISTS search_vector TSVECTOR;

-- 2. Créer une fonction pour générer le search_vector
CREATE OR REPLACE FUNCTION procedures_search_vector_update() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('french', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('french', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('french', COALESCE(regexp_replace(NEW.content, '<[^>]+>', '', 'g'), '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Créer un trigger pour mise à jour automatique lors de INSERT/UPDATE
DROP TRIGGER IF EXISTS procedures_search_vector_trigger ON procedures;
CREATE TRIGGER procedures_search_vector_trigger
    BEFORE INSERT OR UPDATE OF title, description, content
    ON procedures
    FOR EACH ROW
    EXECUTE FUNCTION procedures_search_vector_update();

-- 4. Mettre à jour les search_vector existants
UPDATE procedures SET search_vector =
    setweight(to_tsvector('french', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('french', COALESCE(description, '')), 'B') ||
    setweight(to_tsvector('french', COALESCE(regexp_replace(content, '<[^>]+>', '', 'g'), '')), 'C')
WHERE search_vector IS NULL OR search_vector = '';

-- 5. Créer un index GIN pour performance optimale
CREATE INDEX IF NOT EXISTS idx_procedures_search_vector ON procedures USING GIN(search_vector);

-- 6. Optionnel : Créer un index pour tri par pertinence
CREATE INDEX IF NOT EXISTS idx_procedures_title_trigram ON procedures USING gin(title gin_trgm_ops);

-- Note: L'extension pg_trgm doit être activée pour l'index trigram
-- Si pas encore activée : CREATE EXTENSION IF NOT EXISTS pg_trgm;
