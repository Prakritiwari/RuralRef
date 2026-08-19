-- ============================================================================
-- Migration 003: Row Level Security (RLS) & Realtime Publication
-- Description: Enforces table policies by role and enables Supabase Realtime
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE phcs ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospitals ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospital_resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE referral_resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambulances ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambulance_locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 1. Profiles Policies
CREATE POLICY "Public profiles are readable by authenticated users"
    ON profiles FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Users can update their own profile"
    ON profiles FOR UPDATE
    TO authenticated
    USING (auth_user_id = auth.uid());

-- 2. PHCs Policies (Readable by authenticated users, editable by PHC/Admin)
CREATE POLICY "PHCs viewable by all authenticated users"
    ON phcs FOR SELECT
    TO authenticated
    USING (true);

-- 3. Hospitals Policies (Readable by all authenticated, manageable by Hospital Admins)
CREATE POLICY "Hospitals viewable by all authenticated users"
    ON hospitals FOR SELECT
    TO authenticated
    USING (true);

-- 4. Resources Catalog Policies
CREATE POLICY "Resource catalog viewable by all authenticated users"
    ON resources FOR SELECT
    TO authenticated
    USING (true);

-- 5. Hospital Resources Policies
CREATE POLICY "Hospital resources viewable by all authenticated users"
    ON hospital_resources FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Hospital admins can update their hospital resources"
    ON hospital_resources FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.auth_user_id = auth.uid()
            AND (profiles.role = 'ADMIN' OR (profiles.role = 'HOSPITAL' AND profiles.organization_id = hospital_resources.hospital_id))
        )
    );

-- 6. Patients Policies (Viewable/Creatable by PHC that created them)
CREATE POLICY "Patients viewable by PHC staff and receiving hospitals"
    ON patients FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Patients insertable by PHC staff"
    ON patients FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.auth_user_id = auth.uid()
            AND profiles.role IN ('PHC', 'ADMIN')
        )
    );

-- 7. Referrals Policies
CREATE POLICY "Referrals viewable by participating PHC, Hospital, and Admin"
    ON referrals FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.auth_user_id = auth.uid()
            AND (
                profiles.role = 'ADMIN'
                OR (profiles.role = 'PHC' AND profiles.organization_id = referrals.phc_id)
                OR (profiles.role = 'HOSPITAL' AND (referrals.hospital_id IS NULL OR profiles.organization_id = referrals.hospital_id))
            )
        )
    );

CREATE POLICY "Referrals insertable by PHC staff"
    ON referrals FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.auth_user_id = auth.uid()
            AND profiles.role IN ('PHC', 'ADMIN')
        )
    );

CREATE POLICY "Referrals updatable by participating hospital and PHC"
    ON referrals FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.auth_user_id = auth.uid()
            AND (
                profiles.role = 'ADMIN'
                OR (profiles.role = 'HOSPITAL' AND profiles.organization_id = referrals.hospital_id)
                OR (profiles.role = 'PHC' AND profiles.organization_id = referrals.phc_id)
            )
        )
    );

-- 8. Referral Resources Policies
CREATE POLICY "Referral resources viewable by authenticated users"
    ON referral_resources FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Referral resources insertable by PHC staff"
    ON referral_resources FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- 9. Ambulances Policies
CREATE POLICY "Ambulances viewable by all authenticated users"
    ON ambulances FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Ambulances updatable by hospital staff and admin"
    ON ambulances FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.auth_user_id = auth.uid()
            AND (profiles.role = 'ADMIN' OR profiles.role = 'HOSPITAL')
        )
    );

-- 10. Ambulance Locations Policies
CREATE POLICY "Ambulance locations viewable by authenticated users"
    ON ambulance_locations FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Ambulance locations insertable by authorized services"
    ON ambulance_locations FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- 11. Audit Logs Policies
CREATE POLICY "Audit logs readable by admins"
    ON audit_logs FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.auth_user_id = auth.uid()
            AND profiles.role = 'ADMIN'
        )
    );

CREATE POLICY "Audit logs insertable by all authenticated users"
    ON audit_logs FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- ============================================================================
-- Enable Supabase Realtime on key tables for instant live updates
-- ============================================================================
DO $$
BEGIN
    -- Add tables to realtime publication if supabase_realtime publication exists
    IF EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'supabase_realtime') THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE referrals;
        ALTER PUBLICATION supabase_realtime ADD TABLE hospital_resources;
        ALTER PUBLICATION supabase_realtime ADD TABLE ambulances;
        ALTER PUBLICATION supabase_realtime ADD TABLE ambulance_locations;
    END IF;
END $$;
