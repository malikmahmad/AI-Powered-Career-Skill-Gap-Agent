-- ============================================================
-- SkillGap AI — Supabase Database Schema
-- Run this in your Supabase SQL Editor to set up the database.
-- https://supabase.com/dashboard → SQL Editor → New Query
-- ============================================================

-- Enable UUID extension (already enabled in most Supabase projects)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Profiles Table ────────────────────────────────────────────────────────────
-- Stores one row per analysis run. Multiple runs per user are allowed.

CREATE TABLE IF NOT EXISTS public."Profiles" (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         TEXT        NOT NULL,
    user_email      TEXT        NOT NULL DEFAULT 'anonymous',
    resume_text     TEXT,
    target_role     TEXT        NOT NULL DEFAULT 'unknown',
    gap_matrix      JSONB,
    readiness_score INTEGER     CHECK (readiness_score >= 0 AND readiness_score <= 100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Indexes ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_profiles_user_id    ON public."Profiles" (user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_user_email ON public."Profiles" (user_email);
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON public."Profiles" (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_target_role ON public."Profiles" (target_role);

-- ── Row Level Security ────────────────────────────────────────────────────────
-- Enables RLS so users can only read their own data.
-- The app uses the anon key, so reads go through these policies.

ALTER TABLE public."Profiles" ENABLE ROW LEVEL SECURITY;

-- Allow the service/anon role to insert (analysis saves)
CREATE POLICY "Allow insert for all" ON public."Profiles"
    FOR INSERT
    WITH CHECK (true);

-- Allow reading all rows (for admin telemetry — tighten in production)
CREATE POLICY "Allow read for all" ON public."Profiles"
    FOR SELECT
    USING (true);

-- ── Helper View ───────────────────────────────────────────────────────────────
-- Useful for admin dashboard telemetry queries.

CREATE OR REPLACE VIEW public.analysis_summary AS
SELECT
    target_role,
    COUNT(*)                            AS total_analyses,
    COUNT(DISTINCT user_email)          AS unique_users,
    ROUND(AVG(readiness_score), 1)      AS avg_readiness_score,
    MAX(created_at)                     AS last_analysis_at
FROM public."Profiles"
GROUP BY target_role
ORDER BY total_analyses DESC;

-- ── Sample Verification Query ─────────────────────────────────────────────────
-- Run this after setup to confirm everything is working:
-- SELECT * FROM public.analysis_summary;
-- SELECT COUNT(*) FROM public."Profiles";
