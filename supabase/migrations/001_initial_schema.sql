-- ============================================================================
-- Migration 001: Initial Schema for Rural Emergency Coordination
-- Description: Defines core tables, foreign keys, check constraints, and indexes
-- ============================================================================

-- Enable UUID extension & PostGIS (if available on Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Profiles Table (Linked to Supabase auth.users)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id UUID UNIQUE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('PHC', 'HOSPITAL', 'ADMIN', 'PATIENT')),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50) DEFAULT '',
    organization_id UUID, -- References phcs(id) or hospitals(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Primary Health Centres (PHCs)
CREATE TABLE IF NOT EXISTS phcs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Maharashtra',
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    contact_phone VARCHAR(50) NOT NULL,
    contact_email VARCHAR(255) DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Hospitals
CREATE TABLE IF NOT EXISTS hospitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Maharashtra',
    level VARCHAR(50) NOT NULL DEFAULT 'District Hospital', -- 'District Hospital', 'Tertiary Care', 'Sub-District Hospital'
    address TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(255) DEFAULT '',
    emergency_available BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Patients
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phc_id UUID REFERENCES phcs(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL CHECK (age >= 0 AND age <= 130),
    gender VARCHAR(20) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    phone VARCHAR(50) DEFAULT '',
    blood_group VARCHAR(10) DEFAULT '',
    emergency_summary TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Referrals
CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_number VARCHAR(50) UNIQUE NOT NULL,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE RESTRICT,
    phc_id UUID NOT NULL REFERENCES phcs(id) ON DELETE RESTRICT,
    hospital_id UUID REFERENCES hospitals(id) ON DELETE SET NULL,
    urgency VARCHAR(20) NOT NULL DEFAULT 'MEDIUM' CHECK (urgency IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    clinical_summary TEXT NOT NULL DEFAULT '',
    specialist_needed VARCHAR(100) DEFAULT '',
    notes TEXT DEFAULT '',
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING' CHECK (
        status IN (
            'PENDING',
            'ACCEPTED',
            'REJECTED',
            'AMBULANCE_ASSIGNED',
            'AMBULANCE_EN_ROUTE',
            'PATIENT_PICKED_UP',
            'PATIENT_IN_TRANSIT',
            'ARRIVED',
            'COMPLETED',
            'CANCELLED'
        )
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- 6. Ambulances
CREATE TABLE IF NOT EXISTS ambulances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id UUID NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    vehicle_number VARCHAR(50) UNIQUE NOT NULL,
    driver_name VARCHAR(255) NOT NULL,
    driver_phone VARCHAR(50) NOT NULL,
    ambulance_type VARCHAR(50) NOT NULL DEFAULT 'ADVANCED_LIFE_SUPPORT' CHECK (
        ambulance_type IN ('BASIC_LIFE_SUPPORT', 'ADVANCED_LIFE_SUPPORT', 'PATIENT_TRANSPORT')
    ),
    status VARCHAR(30) NOT NULL DEFAULT 'AVAILABLE' CHECK (
        status IN (
            'AVAILABLE',
            'ASSIGNED',
            'EN_ROUTE_TO_PHC',
            'PATIENT_PICKED_UP',
            'TRANSPORTING',
            'ARRIVED',
            'OFFLINE'
        )
    ),
    current_latitude DOUBLE PRECISION NOT NULL,
    current_longitude DOUBLE PRECISION NOT NULL,
    active_referral_id UUID REFERENCES referrals(id) ON DELETE SET NULL,
    last_location_update TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Ambulance Locations (Telemetry Stream)
CREATE TABLE IF NOT EXISTS ambulance_locations (
    id BIGSERIAL PRIMARY KEY,
    ambulance_id UUID NOT NULL REFERENCES ambulances(id) ON DELETE CASCADE,
    referral_id UUID REFERENCES referrals(id) ON DELETE SET NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    speed FLOAT DEFAULT 0.0,
    heading FLOAT DEFAULT 0.0,
    accuracy FLOAT DEFAULT 5.0,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Audit Logs (Healthcare Coordination Trail)
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor_user_id UUID,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for high-frequency queries
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_org ON profiles(organization_id);
CREATE INDEX IF NOT EXISTS idx_phcs_location ON phcs(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_hospitals_location ON hospitals(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_referrals_status ON referrals(status);
CREATE INDEX IF NOT EXISTS idx_referrals_phc ON referrals(phc_id);
CREATE INDEX IF NOT EXISTS idx_referrals_hospital ON referrals(hospital_id);
CREATE INDEX IF NOT EXISTS idx_ambulances_status ON ambulances(status);
CREATE INDEX IF NOT EXISTS idx_ambulances_hospital ON ambulances(hospital_id);
CREATE INDEX IF NOT EXISTS idx_amb_locations_amb_time ON ambulance_locations(ambulance_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at DESC);
