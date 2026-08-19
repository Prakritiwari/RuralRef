-- ============================================================================
-- Migration 002: Normalized Resource Catalog & Inventory Management
-- Description: Creates resources, hospital_resources, and referral_resources
-- ============================================================================

-- 1. Resources Catalog Table
CREATE TABLE IF NOT EXISTS resources (
    id VARCHAR(50) PRIMARY KEY, -- e.g. 'ICU', 'VENTILATOR', 'OXYGEN', 'BLOOD_O_POS', 'CT_SCAN'
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('BED', 'EQUIPMENT', 'SPECIALTY', 'DIAGNOSTIC', 'BLOOD')),
    unit VARCHAR(50) NOT NULL DEFAULT 'UNIT', -- 'BED', 'CYLINDER', 'UNIT', 'DOCTOR'
    description TEXT DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Hospital Resources Inventory
CREATE TABLE IF NOT EXISTS hospital_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id UUID NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    resource_id VARCHAR(50) NOT NULL REFERENCES resources(id) ON DELETE RESTRICT,
    total_quantity INT NOT NULL DEFAULT 0 CHECK (total_quantity >= 0),
    available_quantity INT NOT NULL DEFAULT 0 CHECK (available_quantity >= 0),
    reserved_quantity INT NOT NULL DEFAULT 0 CHECK (reserved_quantity >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE', 'LIMITED', 'UNAVAILABLE')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Consistency constraint: available + reserved must never exceed total
    CONSTRAINT chk_quantity_consistency CHECK (available_quantity + reserved_quantity <= total_quantity),
    -- Each hospital has at most one inventory entry per resource
    CONSTRAINT uq_hospital_resource UNIQUE (hospital_id, resource_id)
);

-- 3. Referral Resource Requirements
CREATE TABLE IF NOT EXISTS referral_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_id UUID NOT NULL REFERENCES referrals(id) ON DELETE CASCADE,
    resource_id VARCHAR(50) NOT NULL REFERENCES resources(id) ON DELETE RESTRICT,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    is_critical BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_referral_resource UNIQUE (referral_id, resource_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_hosp_res_hospital ON hospital_resources(hospital_id);
CREATE INDEX IF NOT EXISTS idx_hosp_res_resource ON hospital_resources(resource_id);
CREATE INDEX IF NOT EXISTS idx_hosp_res_status ON hospital_resources(status);
CREATE INDEX IF NOT EXISTS idx_ref_res_referral ON referral_resources(referral_id);
