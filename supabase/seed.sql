-- ============================================================================
-- Supabase Development Seed Data
-- ============================================================================

-- 1. Insert Standard Resource Catalog
INSERT INTO resources (id, name, category, unit, description) VALUES
('ICU', 'Intensive Care Unit (ICU) Bed', 'BED', 'BED', 'Fully monitored critical care bed with vital signs monitor and central infusion lines'),
('VENTILATOR', 'Invasive Mechanical Ventilator', 'EQUIPMENT', 'UNIT', 'Advanced positive-pressure ventilator for respiratory failure management'),
('OXYGEN', 'High-Flow Oxygen Port / Cylinder', 'EQUIPMENT', 'CYLINDER', 'Continuous medical oxygen supply with flowmeter and humidifier'),
('BLOOD_O_POS', 'O+ Packed Red Blood Cells (PRBC)', 'BLOOD', 'UNIT', 'Universal recipient PRBC units stored at 2-6°C in blood bank'),
('BLOOD_AB_NEG', 'AB- Fresh Frozen Plasma', 'BLOOD', 'UNIT', 'Plasma units for coagulopathy and trauma resuscitation'),
('CT_SCAN', '128-Slice Multi-Detector CT Scan', 'DIAGNOSTIC', 'UNIT', 'Fast helical computed tomography scanner for emergency trauma/stroke triage'),
('MRI', '1.5 Tesla Emergency MRI', 'DIAGNOSTIC', 'UNIT', 'Magnetic resonance imaging for neurological and soft tissue assessment'),
('EMERGENCY_BED', 'Emergency Triage & Resuscitation Bed', 'BED', 'BED', 'Acute resuscitation bay equipped for cardiac arrest and polytrauma'),
('OPERATION_THEATRE', 'Emergency Operation Theatre (OT)', 'SPECIALTY', 'UNIT', 'Surgical suite staffed 24x7 for emergency laparotomy and trauma surgery'),
('CARDIOLOGY', 'Interventional Cardiology / Cath Lab', 'SPECIALTY', 'DOCTOR', 'Primary PCI and STEMI intervention service with on-call cardiologist'),
('NEUROLOGY', 'Emergency Neurosurgery Service', 'SPECIALTY', 'DOCTOR', 'Neurosurgical intervention for acute intracranial hemorrhage and traumatic brain injury'),
('TRAUMA_CARE', 'Level 2 Polytrauma Team', 'SPECIALTY', 'DOCTOR', 'Multidisciplinary trauma surgery, orthopedic, and anesthesia on-call response team')
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    category = EXCLUDED.category,
    unit = EXCLUDED.unit,
    description = EXCLUDED.description;

-- 2. Insert Primary Health Centres (PHCs)
INSERT INTO phcs (id, name, code, address, district, state, latitude, longitude, contact_phone, contact_email) VALUES
('a0000001-0000-0000-0000-000000000001', 'Palghar Rural Health Centre', 'PHC-PLG-01', 'Gram Panchayat Road, Palghar West', 'Palghar', 'Maharashtra', 19.6967, 72.7699, '+91-9823001122', 'phc.palghar@ruralreflink.gov'),
('a0000001-0000-0000-0000-000000000002', 'Dahanu Tribal Primary Health Centre', 'PHC-DHN-02', 'Coastal Highway, Dahanu Rural', 'Palghar', 'Maharashtra', 19.9700, 72.7300, '+91-9823003344', 'phc.dahanu@ruralreflink.gov'),
('a0000001-0000-0000-0000-000000000003', 'Manor Community Health Centre', 'PHC-MNR-03', 'Mumbai-Ahmedabad Highway Junction, Manor', 'Palghar', 'Maharashtra', 19.7483, 72.9150, '+91-9823005566', 'phc.manor@ruralreflink.gov')
ON CONFLICT (code) DO NOTHING;

-- 3. Insert Hospitals
INSERT INTO hospitals (id, name, code, district, state, level, address, latitude, longitude, phone, email, emergency_available) VALUES
('b0000001-0000-0000-0000-000000000001', 'Sahyadri District Care Hospital', 'HOSP-SYD-01', 'Palghar', 'Maharashtra', 'District Hospital', 'Civil Hospital Complex, Kacheri Road, Palghar', 19.6980, 72.7750, '+91-2525-252001', 'emergency@sahyadri-palghar.org', TRUE),
('b0000001-0000-0000-0000-000000000002', 'Konkan Critical Care & Trauma Centre', 'HOSP-KNK-02', 'Thane', 'Maharashtra', 'Tertiary Care', 'Ghodbunder Road, Majiwada, Thane West', 19.2183, 72.9781, '+91-22-25801122', 'triage@konkancritical.org', TRUE),
('b0000001-0000-0000-0000-000000000003', 'JanSeva Sub-District Hospital', 'HOSP-JSV-03', 'Palghar', 'Maharashtra', 'Sub-District Hospital', 'Station Road, Boisar East', 19.7990, 72.7560, '+91-2525-271000', 'referral@janseva.org', TRUE),
('b0000001-0000-0000-0000-000000000004', 'Apex Multi-Speciality Medical College Hospital', 'HOSP-APX-04', 'Nashik', 'Maharashtra', 'Tertiary Care', 'Mumbai-Agra Highway, Nashik', 19.9975, 73.7898, '+91-253-2400500', 'emergency@apexnashik.org', TRUE)
ON CONFLICT (code) DO NOTHING;

-- 4. Insert Hospital Resource Inventories
-- Hospital 1: Sahyadri District Care Hospital (Good ICU, High Oxygen, Limited Vent)
INSERT INTO hospital_resources (hospital_id, resource_id, total_quantity, available_quantity, reserved_quantity, status) VALUES
('b0000001-0000-0000-0000-000000000001', 'ICU', 8, 4, 2, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000001', 'VENTILATOR', 5, 3, 1, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000001', 'OXYGEN', 25, 18, 5, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000001', 'BLOOD_O_POS', 10, 8, 1, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000001', 'CT_SCAN', 1, 1, 0, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000001', 'EMERGENCY_BED', 12, 5, 4, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000001', 'CARDIOLOGY', 2, 2, 0, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000001', 'TRAUMA_CARE', 2, 1, 1, 'AVAILABLE')
ON CONFLICT (hospital_id, resource_id) DO NOTHING;

-- Hospital 2: Konkan Critical Care & Trauma Centre (High Capacity Tertiary)
INSERT INTO hospital_resources (hospital_id, resource_id, total_quantity, available_quantity, reserved_quantity, status) VALUES
('b0000001-0000-0000-0000-000000000002', 'ICU', 20, 12, 5, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000002', 'VENTILATOR', 12, 7, 3, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000002', 'OXYGEN', 50, 42, 6, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000002', 'BLOOD_O_POS', 25, 20, 2, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000002', 'CT_SCAN', 2, 2, 0, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000002', 'MRI', 1, 1, 0, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000002', 'OPERATION_THEATRE', 4, 2, 1, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000002', 'CARDIOLOGY', 4, 3, 1, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000002', 'NEUROLOGY', 3, 2, 1, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000002', 'TRAUMA_CARE', 4, 3, 1, 'AVAILABLE')
ON CONFLICT (hospital_id, resource_id) DO NOTHING;

-- Hospital 3: JanSeva Sub-District Hospital (No Ventilator, Limited ICU - For recommendation filter testing)
INSERT INTO hospital_resources (hospital_id, resource_id, total_quantity, available_quantity, reserved_quantity, status) VALUES
('b0000001-0000-0000-0000-000000000003', 'ICU', 3, 1, 2, 'LIMITED'),
('b0000001-0000-0000-0000-000000000003', 'VENTILATOR', 2, 0, 2, 'UNAVAILABLE'), -- 0 available ventilators
('b0000001-0000-0000-0000-000000000003', 'OXYGEN', 10, 6, 2, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000003', 'BLOOD_O_POS', 4, 3, 1, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000003', 'EMERGENCY_BED', 6, 2, 2, 'AVAILABLE')
ON CONFLICT (hospital_id, resource_id) DO NOTHING;

-- Hospital 4: Apex Multi-Speciality Medical College Hospital
INSERT INTO hospital_resources (hospital_id, resource_id, total_quantity, available_quantity, reserved_quantity, status) VALUES
('b0000001-0000-0000-0000-000000000004', 'ICU', 25, 14, 8, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000004', 'VENTILATOR', 15, 9, 4, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000004', 'OXYGEN', 60, 48, 10, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000004', 'BLOOD_O_POS', 30, 25, 3, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000004', 'CT_SCAN', 2, 2, 0, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000004', 'MRI', 2, 1, 1, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000004', 'CARDIOLOGY', 5, 4, 1, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000004', 'NEUROLOGY', 4, 3, 1, 'AVAILABLE'),
('b0000001-0000-0000-0000-000000000004', 'TRAUMA_CARE', 5, 4, 1, 'AVAILABLE')
ON CONFLICT (hospital_id, resource_id) DO NOTHING;

-- 5. Insert Ambulances
INSERT INTO ambulances (id, hospital_id, vehicle_number, driver_name, driver_phone, ambulance_type, status, current_latitude, current_longitude) VALUES
('c0000001-0000-0000-0000-000000000001', 'b0000001-0000-0000-0000-000000000001', 'MH-04-AZ-1001', 'Ramesh Shinde', '+91-9876543210', 'ADVANCED_LIFE_SUPPORT', 'AVAILABLE', 19.6980, 72.7750),
('c0000001-0000-0000-0000-000000000002', 'b0000001-0000-0000-0000-000000000001', 'MH-04-AZ-1002', 'Anil Patil', '+91-9876543211', 'BASIC_LIFE_SUPPORT', 'AVAILABLE', 19.6980, 72.7750),
('c0000001-0000-0000-0000-000000000003', 'b0000001-0000-0000-0000-000000000002', 'MH-04-BL-2001', 'Vikram Yadav', '+91-9876543212', 'ADVANCED_LIFE_SUPPORT', 'AVAILABLE', 19.2183, 72.9781),
('c0000001-0000-0000-0000-000000000004', 'b0000001-0000-0000-0000-000000000002', 'MH-04-BL-2002', 'Santosh Pawar', '+91-9876543213', 'PATIENT_TRANSPORT', 'AVAILABLE', 19.2183, 72.9781),
('c0000001-0000-0000-0000-000000000005', 'b0000001-0000-0000-0000-000000000003', 'MH-04-CR-3001', 'Deepak More', '+91-9876543214', 'BASIC_LIFE_SUPPORT', 'AVAILABLE', 19.7990, 72.7560),
('c0000001-0000-0000-0000-000000000006', 'b0000001-0000-0000-0000-000000000004', 'MH-15-DX-4001', 'Suresh Jadhav', '+91-9876543215', 'ADVANCED_LIFE_SUPPORT', 'AVAILABLE', 19.9975, 73.7898)
ON CONFLICT (vehicle_number) DO NOTHING;

-- 6. Insert Demo Patients
INSERT INTO patients (id, phc_id, name, age, gender, phone, blood_group, emergency_summary) VALUES
('d0000001-0000-0000-0000-000000000001', 'a0000001-0000-0000-0000-000000000001', 'Sunita Ramdas Gaikwad', 48, 'Female', '+91-9988776655', 'O+', 'Acute respiratory distress syndrome (ARDS), SpO2 78% on room air, severe dyspnea, history of bronchial asthma'),
('d0000001-0000-0000-0000-000000000002', 'a0000001-0000-0000-0000-000000000001', 'Tukaram Laxman Bhor', 62, 'Male', '+91-9988776656', 'B+', 'Acute anterior wall STEMI, crushing retrosternal chest pain radiating to left jaw, cardiogenic shock with BP 80/50 mmHg'),
('d0000001-0000-0000-0000-000000000003', 'a0000001-0000-0000-0000-000000000002', 'Kiran Vijay Mhatre', 29, 'Male', '+91-9988776657', 'A+', 'Polytrauma following highway vehicular collision. Suspected blunt abdominal trauma with hemoperitoneum and right femur fracture')
ON CONFLICT (id) DO NOTHING;

-- 7. Insert Profiles for Demo Users
INSERT INTO profiles (id, role, name, email, phone, organization_id) VALUES
('e0000001-0000-0000-0000-000000000001', 'PHC', 'Dr. Priya Sharma (PHC Medical Officer)', 'doctor@demo.com', '+91-9000000001', 'a0000001-0000-0000-0000-000000000001'),
('e0000001-0000-0000-0000-000000000002', 'HOSPITAL', 'Dr. Arvind Deshmukh (Hospital Admin)', 'hospital@demo.com', '+91-9000000002', 'b0000001-0000-0000-0000-000000000001'),
('e0000001-0000-0000-0000-000000000003', 'ADMIN', 'System Administrator', 'admin@demo.com', '+91-9000000000', NULL),
('e0000001-0000-0000-0000-000000000004', 'PATIENT', 'Sunita Ramdas Gaikwad', 'patient@demo.com', '+91-9988776655', NULL)
ON CONFLICT (email) DO NOTHING;
