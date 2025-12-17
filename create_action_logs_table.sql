-- Create action_logs table for audit tracking
CREATE TABLE IF NOT EXISTS action_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    entity_name VARCHAR(500),
    details TEXT,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_action_logs_user_id ON action_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_action_logs_action_type ON action_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_action_logs_entity_type ON action_logs(entity_type);
CREATE INDEX IF NOT EXISTS idx_action_logs_entity_id ON action_logs(entity_id);
CREATE INDEX IF NOT EXISTS idx_action_logs_created_at ON action_logs(created_at);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_entity_lookup ON action_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_user_action ON action_logs(user_id, action_type);
CREATE INDEX IF NOT EXISTS idx_date_action ON action_logs(created_at, action_type);
