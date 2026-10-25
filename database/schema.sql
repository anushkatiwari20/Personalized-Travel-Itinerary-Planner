-- ============================================================
-- Supabase SQL Schema
-- Personalized Travel Itinerary Planner
-- Run this whole file in Supabase -> SQL Editor -> New -> Run
-- Expected result: "Success. No rows returned"
-- Creates 6 tables: users, trips, itineraries, preferences,
--                   saved_places, history
-- ============================================================

-- ---------- EXTENSIONS ----------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------- USERS TABLE ----------
CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    name          VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ---------- TRIPS TABLE ----------
CREATE TABLE IF NOT EXISTS trips (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id              UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    destination          VARCHAR(255) NOT NULL,
    start_date           DATE NOT NULL,
    end_date             DATE NOT NULL,
    travel_style         VARCHAR(50) NOT NULL DEFAULT 'cultural',
    interests            TEXT[] NOT NULL DEFAULT '{}',
    group_size           INTEGER NOT NULL DEFAULT 1,
    pace                 VARCHAR(20) NOT NULL DEFAULT 'moderate',
    budget_per_day       NUMERIC(10,2) NOT NULL DEFAULT 2000,
    dietary_restrictions TEXT[] DEFAULT '{}',
    mobility_concerns    TEXT,
    notes                TEXT,
    status               VARCHAR(20) NOT NULL DEFAULT 'draft',  -- draft | generated | archived
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trips_user_id ON trips(user_id);
CREATE INDEX IF NOT EXISTS idx_trips_created_at ON trips(created_at DESC);

-- ---------- ITINERARIES TABLE ----------
CREATE TABLE IF NOT EXISTS itineraries (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id              UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    user_id              UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    destination          VARCHAR(255) NOT NULL,
    duration_days        INTEGER NOT NULL,
    total_estimated_cost NUMERIC(12,2) DEFAULT 0,
    itinerary_days       JSONB NOT NULL DEFAULT '[]'::jsonb,
    summary              TEXT,
    ai_provider          VARCHAR(50),
    version              INTEGER NOT NULL DEFAULT 1,
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_itineraries_trip_id ON itineraries(trip_id);
CREATE INDEX IF NOT EXISTS idx_itineraries_user_id ON itineraries(user_id);

-- ---------- PREFERENCES TABLE ----------
CREATE TABLE IF NOT EXISTS preferences (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id              UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    travel_style         VARCHAR(50) DEFAULT 'cultural',
    interests            TEXT[] DEFAULT '{}',
    pace                 VARCHAR(20) DEFAULT 'moderate',
    budget_per_day       NUMERIC(10,2) DEFAULT 2000,
    dietary_restrictions TEXT[] DEFAULT '{}',
    currency             VARCHAR(10) DEFAULT 'INR',
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ---------- SAVED PLACES TABLE ----------
CREATE TABLE IF NOT EXISTS saved_places (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trip_id     UUID REFERENCES trips(id) ON DELETE SET NULL,
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    category    VARCHAR(50),          -- attraction | dining | stay | activity
    time_slot   VARCHAR(20),          -- morning | afternoon | evening
    destination VARCHAR(255),
    image_url   TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_saved_places_user_id ON saved_places(user_id);

-- ---------- HISTORY TABLE ----------
CREATE TABLE IF NOT EXISTS history (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trip_id    UUID REFERENCES trips(id) ON DELETE SET NULL,
    action     VARCHAR(50) NOT NULL,   -- trip_created | itinerary_generated | itinerary_regenerated | trip_deleted | place_saved | exported
    details    JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id);
CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at DESC);

-- ---------- updated_at TRIGGER ----------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated ON users;
CREATE TRIGGER trg_users_updated BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_trips_updated ON trips;
CREATE TRIGGER trg_trips_updated BEFORE UPDATE ON trips
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_itineraries_updated ON itineraries;
CREATE TRIGGER trg_itineraries_updated BEFORE UPDATE ON itineraries
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_preferences_updated ON preferences;
CREATE TRIGGER trg_preferences_updated BEFORE UPDATE ON preferences
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------- ROW LEVEL SECURITY ----------
-- The FastAPI backend talks to Supabase with the service_role key
-- (bypasses RLS). RLS is enabled so the anon key alone cannot read data.
ALTER TABLE users        ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips        ENABLE ROW LEVEL SECURITY;
ALTER TABLE itineraries  ENABLE ROW LEVEL SECURITY;
ALTER TABLE preferences  ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_places ENABLE ROW LEVEL SECURITY;
ALTER TABLE history      ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service role full access users" ON users;
CREATE POLICY "service role full access users" ON users
    FOR ALL USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

DROP POLICY IF EXISTS "service role full access trips" ON trips;
CREATE POLICY "service role full access trips" ON trips
    FOR ALL USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

DROP POLICY IF EXISTS "service role full access itineraries" ON itineraries;
CREATE POLICY "service role full access itineraries" ON itineraries
    FOR ALL USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

DROP POLICY IF EXISTS "service role full access preferences" ON preferences;
CREATE POLICY "service role full access preferences" ON preferences
    FOR ALL USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

DROP POLICY IF EXISTS "service role full access saved_places" ON saved_places;
CREATE POLICY "service role full access saved_places" ON saved_places
    FOR ALL USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

DROP POLICY IF EXISTS "service role full access history" ON history;
CREATE POLICY "service role full access history" ON history
    FOR ALL USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

-- ---------- DONE ----------
-- Verify: Table Editor should now list
--   history, itineraries, preferences, saved_places, trips, users
