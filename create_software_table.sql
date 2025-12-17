-- Migration SQL pour créer la table Software

CREATE TABLE IF NOT EXISTS software (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    url VARCHAR(500) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    added_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_free BOOLEAN DEFAULT TRUE,
    platform VARCHAR(100),
    useful_count INTEGER DEFAULT 0
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_software_name ON software(name);
CREATE INDEX IF NOT EXISTS idx_software_category ON software(category_id);
CREATE INDEX IF NOT EXISTS idx_software_created_at ON software(created_at);
CREATE INDEX IF NOT EXISTS idx_software_platform ON software(platform);

-- Commentaires
COMMENT ON TABLE software IS 'Table des logiciels utiles pour le service IT';
COMMENT ON COLUMN software.name IS 'Nom du logiciel';
COMMENT ON COLUMN software.description IS 'Description du logiciel et de son utilité';
COMMENT ON COLUMN software.url IS 'URL vers le site officiel ou page de téléchargement';
COMMENT ON COLUMN software.category_id IS 'Catégorie du logiciel';
COMMENT ON COLUMN software.added_by IS 'Utilisateur qui a ajouté le logiciel';
COMMENT ON COLUMN software.is_free IS 'Le logiciel est-il gratuit';
COMMENT ON COLUMN software.platform IS 'Plateforme(s) supportée(s)';
COMMENT ON COLUMN software.useful_count IS 'Nombre de votes utiles';
