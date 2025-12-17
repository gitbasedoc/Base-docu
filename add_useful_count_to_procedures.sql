-- Add useful_count column to procedures table
ALTER TABLE procedures ADD COLUMN IF NOT EXISTS useful_count INTEGER DEFAULT 0;

-- Update existing procedures to have 0 as default
UPDATE procedures SET useful_count = 0 WHERE useful_count IS NULL;
