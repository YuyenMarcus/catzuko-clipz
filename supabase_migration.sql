-- Supabase PostgreSQL Migration Script
-- Run this in Supabase SQL Editor to create all required tables

-- Clips table
CREATE TABLE IF NOT EXISTS clips (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    video_path TEXT NOT NULL,
    caption_path TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    platform TEXT NOT NULL,
    caption TEXT,
    start_time REAL,
    end_time REAL,
    reason TEXT,
    storage_url TEXT,
    posted_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Logs table
CREATE TABLE IF NOT EXISTS logs (
    id BIGSERIAL PRIMARY KEY,
    level TEXT NOT NULL,
    component TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Posts table
CREATE TABLE IF NOT EXISTS posts (
    id BIGSERIAL PRIMARY KEY,
    clip_id BIGINT REFERENCES clips(id),
    platform TEXT NOT NULL,
    account TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    posted_at TIMESTAMPTZ DEFAULT NOW()
);

-- Heartbeats table (for worker status)
CREATE TABLE IF NOT EXISTS heartbeats (
    worker_id TEXT PRIMARY KEY,
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'online'
);

-- Insert default settings
INSERT INTO settings (key, value) VALUES
    ('auto_posting_enabled', '0'),
    ('auto_posting_tiktok', '0'),
    ('auto_posting_instagram', '0'),
    ('auto_posting_youtube', '0')
ON CONFLICT (key) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_clips_status ON clips(status);
CREATE INDEX IF NOT EXISTS idx_clips_platform ON clips(platform);
CREATE INDEX IF NOT EXISTS idx_clips_created_at ON clips(created_at);
CREATE INDEX IF NOT EXISTS idx_logs_component ON logs(component);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at);
CREATE INDEX IF NOT EXISTS idx_posts_posted_at ON posts(posted_at);

-- Enable Row Level Security (optional, for multi-user)
-- ALTER TABLE clips ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE logs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE heartbeats ENABLE ROW LEVEL SECURITY;

