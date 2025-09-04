-- Archon Database Setup for Supabase
-- Run this in your Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create archon_projects table
CREATE TABLE IF NOT EXISTS archon_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    github_repo TEXT,
    pinned BOOLEAN DEFAULT false,
    features JSONB DEFAULT '{}',
    data JSONB DEFAULT '{}',
    docs JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create archon_tasks table
CREATE TABLE IF NOT EXISTS archon_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'todo',
    assignee TEXT DEFAULT 'User',
    task_order INTEGER DEFAULT 0,
    feature TEXT,
    sources JSONB DEFAULT '[]',
    code_examples JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    archived BOOLEAN DEFAULT false
);

-- Create archon_documents table
CREATE TABLE IF NOT EXISTS archon_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
    document_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content JSONB DEFAULT '{}',
    status TEXT DEFAULT 'draft',
    version TEXT DEFAULT '1.0',
    tags TEXT[] DEFAULT '{}',
    author TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create archon_document_versions table
CREATE TABLE IF NOT EXISTS archon_document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
    document_id UUID,
    field_name TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    content JSONB NOT NULL,
    change_summary TEXT,
    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create archon_sources table
CREATE TABLE IF NOT EXISTS archon_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    url TEXT,
    url_display_name TEXT,
    type TEXT DEFAULT 'documentation',
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create archon_project_sources table
CREATE TABLE IF NOT EXISTS archon_project_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
    source_id UUID REFERENCES archon_sources(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, source_id)
);

-- Create archon_crawled_pages table
CREATE TABLE IF NOT EXISTS archon_crawled_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    content TEXT,
    metadata JSONB DEFAULT '{}',
    crawled_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source_id, url)
);

-- Create archon_code_examples table
CREATE TABLE IF NOT EXISTS archon_code_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    code TEXT NOT NULL,
    language TEXT,
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create archon_prompts table
CREATE TABLE IF NOT EXISTS archon_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    type TEXT DEFAULT 'system',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create archon_settings table
CREATE TABLE IF NOT EXISTS archon_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_archon_tasks_project_id ON archon_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_status ON archon_tasks(status);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_assignee ON archon_tasks(assignee);
CREATE INDEX IF NOT EXISTS idx_archon_documents_project_id ON archon_documents(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_project_id ON archon_document_versions(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_source_id ON archon_crawled_pages(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_source_id ON archon_code_examples(source_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_archon_projects_updated_at BEFORE UPDATE ON archon_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_tasks_updated_at BEFORE UPDATE ON archon_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_documents_updated_at BEFORE UPDATE ON archon_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_sources_updated_at BEFORE UPDATE ON archon_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_prompts_updated_at BEFORE UPDATE ON archon_prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_settings_updated_at BEFORE UPDATE ON archon_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed)
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- Success message
SELECT 'Archon database schema created successfully!' as message;