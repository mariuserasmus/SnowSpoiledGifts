-- Database Migration for WhatsApp Integration
-- Run this on production BEFORE deploying code
-- Command: sqlite3 database/signups.db < database_migration.sql

-- Add phone column to print_service_requests table
ALTER TABLE print_service_requests ADD COLUMN phone TEXT;

-- Create whatsapp_messages table
CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE,
    direction TEXT NOT NULL,  -- 'inbound' or 'outbound'
    from_phone TEXT NOT NULL,
    to_phone TEXT NOT NULL,
    message_text TEXT,
    message_type TEXT DEFAULT 'text',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read INTEGER DEFAULT 0,
    conversation_id TEXT,
    user_id INTEGER,
    quote_id INTEGER,
    quote_type TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (quote_id) REFERENCES custom_design_requests(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversation ON whatsapp_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_timestamp ON whatsapp_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_whatsapp_read ON whatsapp_messages(is_read);
CREATE INDEX IF NOT EXISTS idx_whatsapp_user ON whatsapp_messages(user_id);

-- Verify migration
SELECT 'Migration complete!' as status;
SELECT 'Print service requests table:' as info;
PRAGMA table_info(print_service_requests);
SELECT 'WhatsApp messages table:' as info;
PRAGMA table_info(whatsapp_messages);
