import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, SessionLocal, get_db
from .models import (
    Profile, PHC, Hospital, Resource, HospitalResource,
    Patient, Ambulance, Referral, ReferralResource
)
from .utils.security import hash_password
from .api import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ruralreflink")

def seed_database(db: Session):
    """
    Seeds essential initial dataset if tables are empty.
    """
    # 1. Resources Catalog
    if not db.query(Resource).count():
        logger.info("Seeding resources catalog...")
        standard_resources = [
            Resource(id="ICU", name="Intensive Care Unit (ICU) Bed", category="BED", unit="BED", description="Critical care bed with multi-para monitor and central line infusion"),
            Resource(id="VENTILATOR", name="Invasive Mechanical Ventilator", category="EQUIPMENT", unit="UNIT", description="Positive-pressure ventilator for respiratory failure support"),
            Resource(id="OXYGEN", name="High-Flow Medical Oxygen", category="EQUIPMENT", unit="CYLINDER", description="Continuous high-flow oxygen port and cylinders"),
            Resource(id="BLOOD_O_POS", name="O+ Packed Red Blood Cells (PRBC)", category="BLOOD", unit="UNIT", description="Universal recipient PRBC blood units"),
            Resource(id="BLOOD_AB_NEG", name="AB- Fresh Frozen Plasma", category="BLOOD", unit="UNIT", description="Plasma units for acute coagulopathy and trauma"),
            Resource(id="CT_SCAN", name="128-Slice Multi-Detector CT Scan", category="DIAGNOSTIC", unit="UNIT", description="Helical emergency computed tomography scanner"),
            Resource(id="MRI", name="1.5 Tesla Emergency MRI", category="DIAGNOSTIC", unit="UNIT", description="Magnetic resonance imaging for stroke and spine trauma"),
            Resource(id="EMERGENCY_BED", name="Emergency Resuscitation Bay", category="BED", unit="BED", description="Acute resuscitation bed equipped for cardiac arrest and polytrauma"),
            Resource(id="OPERATION_THEATRE", name="Emergency Operation Theatre (OT)", category="SPECIALTY", unit="UNIT", description="24x7 trauma surgery suite with on-call surgical team"),
            Resource(id="CARDIOLOGY", name="Interventional Cardiology / Cath Lab", category="SPECIALTY", unit="DOCTOR", description="Primary PCI and emergency cardiac catheterization"),
            Resource(id="NEUROLOGY", name="Emergency Neurosurgery Service", category="SPECIALTY", unit="DOCTOR", description="Neurosurgical intervention for intracranial hemorrhage"),
            Resource(id="TRAUMA_CARE", name="Level 2 Polytrauma Response Team", category="SPECIALTY", unit="DOCTOR", description="Multidisciplinary trauma surgery, orthopedic, and anesthesia response team")
        ]
        db.add_all(standard_resources)
        db.commit()

    # 2. PHCs
    if not db.query(PHC).count():
        logger.info("Seeding primary health centres...")
        phcs = [
            PHC(
                id="a0000001-0000-0000-0000-000000000001",
                name="Palghar Rural Health Centre",
                code="PHC-PLG-01",
                address="Gram Panchayat Road, Palghar West",
                district="Palghar",
                state="Maharashtra",
                latitude=19.6967,
                longitude=72.7699,
                contact_phone="+91-9823001122",
                contact_email="phc.palghar@ruralreflink.gov"
            ),
            PHC(
                id="a0000001-0000-0000-0000-000000000002",
                name="Dahanu Tribal Primary Health Centre",
                code="PHC-DHN-02",
                address="Coastal Highway, Dahanu Rural",
                district="Palghar",
                state="Maharashtra",
                latitude=19.9700,
                longitude=72.7300,
                contact_phone="+91-9823003344",
                contact_email="phc.dahanu@ruralreflink.gov"
            ),
            PHC(
                id="a0000001-0000-0000-0000-000000000003",
                name="Manor Community Health Centre",
                code="PHC-MNR-03",
                address="Mumbai-Ahmedabad Highway Junction, Manor",
                district="Palghar",
                state="Maharashtra",
                latitude=19.7483,
                longitude=72.9150,
                contact_phone="+91-9823005566",
                contact_email="phc.manor@ruralreflink.gov"
            )
        ]
        db.add_all(phcs)
        db.commit()

    # 3. Hospitals & Resources
    if not db.query(Hospital).count():
        logger.info("Seeding referral hospitals and initial inventories...")
        h1 = Hospital(
            id="b0000001-0000-0000-0000-000000000001",
            name="Sahyadri District Care Hospital",
            code="HOSP-SYD-01",
            district="Palghar",
            state="Maharashtra",
            level="District Hospital",
            address="Civil Hospital Complex, Kacheri Road, Palghar",
            latitude=19.6980,
            longitude=72.7750,
            phone="+91-2525-252001",
            email="emergency@sahyadri-palghar.org",
            emergency_available=True
        )
        h2 = Hospital(
            id="b0000001-0000-0000-0000-000000000002",
            name="Konkan Critical Care & Trauma Centre",
            code="HOSP-KNK-02",
            district="Thane",
            state="Maharashtra",
            level="Tertiary Care",
            address="Ghodbunder Road, Majiwada, Thane West",
            latitude=19.2183,
            longitude=72.9781,
            phone="+91-22-25801122",
            email="triage@konkancritical.org",
            emergency_available=True
        )
        h3 = Hospital(
            id="b0000001-0000-0000-0000-000000000003",
            name="JanSeva Sub-District Hospital",
            code="HOSP-JSV-03",
            district="Palghar",
            state="Maharashtra",
            level="Sub-District Hospital",
            address="Station Road, Boisar East",
            latitude=19.7990,
            longitude=72.7560,
            phone="+91-2525-271000",
            email="referral@janseva.org",
            emergency_available=True
        )
        h4 = Hospital(
            id="b0000001-0000-0000-0000-000000000004",
            name="Apex Multi-Speciality Medical College Hospital",
            code="HOSP-APX-04",
            district="Nashik",
            state="Maharashtra",
            level="Tertiary Care",
            address="Mumbai-Agra Highway, Nashik",
            latitude=19.9975,
            longitude=73.7898,
            phone="+91-253-2400500",
            email="emergency@apexnashik.org",
            emergency_available=True
        )
        db.add_all([h1, h2, h3, h4])
        db.commit()

        # Inventories
        db.add_all([
            HospitalResource(hospital_id=h1.id, resource_id="ICU", total_quantity=8, available_quantity=4, reserved_quantity=2, status="AVAILABLE"),
            HospitalResource(hospital_id=h1.id, resource_id="VENTILATOR", total_quantity=5, available_quantity=3, reserved_quantity=1, status="AVAILABLE"),
            HospitalResource(hospital_id=h1.id, resource_id="OXYGEN", total_quantity=25, available_quantity=18, reserved_quantity=5, status="AVAILABLE"),
            HospitalResource(hospital_id=h1.id, resource_id="BLOOD_O_POS", total_quantity=10, available_quantity=8, reserved_quantity=1, status="AVAILABLE"),
            HospitalResource(hospital_id=h1.id, resource_id="CT_SCAN", total_quantity=1, available_quantity=1, reserved_quantity=0, status="AVAILABLE"),
            HospitalResource(hospital_id=h1.id, resource_id="CARDIOLOGY", total_quantity=2, available_quantity=2, reserved_quantity=0, status="AVAILABLE"),
        ])

        db.add_all([
            HospitalResource(hospital_id=h2.id, resource_id="ICU", total_quantity=20, available_quantity=12, reserved_quantity=5, status="AVAILABLE"),
            HospitalResource(hospital_id=h2.id, resource_id="VENTILATOR", total_quantity=12, available_quantity=7, reserved_quantity=3, status="AVAILABLE"),
            HospitalResource(hospital_id=h2.id, resource_id="OXYGEN", total_quantity=50, available_quantity=42, reserved_quantity=6, status="AVAILABLE"),
            HospitalResource(hospital_id=h2.id, resource_id="BLOOD_O_POS", total_quantity=25, available_quantity=20, reserved_quantity=2, status="AVAILABLE"),
            HospitalResource(hospital_id=h2.id, resource_id="CT_SCAN", total_quantity=2, available_quantity=2, reserved_quantity=0, status="AVAILABLE"),
            HospitalResource(hospital_id=h2.id, resource_id="MRI", total_quantity=1, available_quantity=1, reserved_quantity=0, status="AVAILABLE"),
            HospitalResource(hospital_id=h2.id, resource_id="CARDIOLOGY", total_quantity=4, available_quantity=3, reserved_quantity=1, status="AVAILABLE"),
            HospitalResource(hospital_id=h2.id, resource_id="NEUROLOGY", total_quantity=3, available_quantity=2, reserved_quantity=1, status="AVAILABLE"),
            HospitalResource(hospital_id=h2.id, resource_id="TRAUMA_CARE", total_quantity=4, available_quantity=3, reserved_quantity=1, status="AVAILABLE"),
        ])

        db.add_all([
            HospitalResource(hospital_id=h3.id, resource_id="ICU", total_quantity=3, available_quantity=1, reserved_quantity=2, status="LIMITED"),
            HospitalResource(hospital_id=h3.id, resource_id="VENTILATOR", total_quantity=2, available_quantity=0, reserved_quantity=2, status="UNAVAILABLE"),
            HospitalResource(hospital_id=h3.id, resource_id="OXYGEN", total_quantity=10, available_quantity=6, reserved_quantity=2, status="AVAILABLE"),
            HospitalResource(hospital_id=h3.id, resource_id="BLOOD_O_POS", total_quantity=4, available_quantity=3, reserved_quantity=1, status="AVAILABLE"),
        ])

        db.add_all([
            HospitalResource(hospital_id=h4.id, resource_id="ICU", total_quantity=25, available_quantity=14, reserved_quantity=8, status="AVAILABLE"),
            HospitalResource(hospital_id=h4.id, resource_id="VENTILATOR", total_quantity=15, available_quantity=9, reserved_quantity=4, status="AVAILABLE"),
            HospitalResource(hospital_id=h4.id, resource_id="OXYGEN", total_quantity=60, available_quantity=48, reserved_quantity=10, status="AVAILABLE"),
            HospitalResource(hospital_id=h4.id, resource_id="BLOOD_O_POS", total_quantity=30, available_quantity=25, reserved_quantity=3, status="AVAILABLE"),
            HospitalResource(hospital_id=h4.id, resource_id="CT_SCAN", total_quantity=2, available_quantity=2, reserved_quantity=0, status="AVAILABLE"),
            HospitalResource(hospital_id=h4.id, resource_id="CARDIOLOGY", total_quantity=5, available_quantity=4, reserved_quantity=1, status="AVAILABLE"),
        ])
        db.commit()

        # Ambulances
        db.add_all([
            Ambulance(id="c0000001-0000-0000-0000-000000000001", hospital_id=h1.id, vehicle_number="MH-04-AZ-1001", driver_name="Ramesh Shinde", driver_phone="+91-9876543210", ambulance_type="ADVANCED_LIFE_SUPPORT", status="AVAILABLE", current_latitude=19.6980, current_longitude=72.7750),
            Ambulance(id="c0000001-0000-0000-0000-000000000002", hospital_id=h1.id, vehicle_number="MH-04-AZ-1002", driver_name="Anil Patil", driver_phone="+91-9876543211", ambulance_type="BASIC_LIFE_SUPPORT", status="AVAILABLE", current_latitude=19.6980, current_longitude=72.7750),
            Ambulance(id="c0000001-0000-0000-0000-000000000003", hospital_id=h2.id, vehicle_number="MH-04-BL-2001", driver_name="Vikram Yadav", driver_phone="+91-9876543212", ambulance_type="ADVANCED_LIFE_SUPPORT", status="AVAILABLE", current_latitude=19.2183, current_longitude=72.9781),
            Ambulance(id="c0000001-0000-0000-0000-000000000004", hospital_id=h2.id, vehicle_number="MH-04-BL-2002", driver_name="Santosh Pawar", driver_phone="+91-9876543213", ambulance_type="PATIENT_TRANSPORT", status="AVAILABLE", current_latitude=19.2183, current_longitude=72.9781),
            Ambulance(id="c0000001-0000-0000-0000-000000000005", hospital_id=h3.id, vehicle_number="MH-04-CR-3001", driver_name="Deepak More", driver_phone="+91-9876543214", ambulance_type="BASIC_LIFE_SUPPORT", status="AVAILABLE", current_latitude=19.7990, current_longitude=72.7560),
            Ambulance(id="c0000001-0000-0000-0000-000000000006", hospital_id=h4.id, vehicle_number="MH-15-DX-4001", driver_name="Suresh Jadhav", driver_phone="+91-9876543215", ambulance_type="ADVANCED_LIFE_SUPPORT", status="AVAILABLE", current_latitude=19.9975, current_longitude=73.7898),
        ])
        db.commit()

    # 4. Patients
    if not db.query(Patient).count():
        logger.info("Seeding patient records...")
        phc1 = db.query(PHC).first()
        patients = [
            Patient(id="d0000001-0000-0000-0000-000000000001", phc_id=phc1.id if phc1 else None, name="Sunita Ramdas Gaikwad", age=48, gender="Female", phone="+91-9988776655", blood_group="O+", emergency_summary="Acute respiratory distress syndrome (ARDS), SpO2 78% on room air, severe dyspnea, history of bronchial asthma"),
            Patient(id="d0000001-0000-0000-0000-000000000002", phc_id=phc1.id if phc1 else None, name="Tukaram Laxman Bhor", age=62, gender="Male", phone="+91-9988776656", blood_group="B+", emergency_summary="Acute anterior wall STEMI, crushing retrosternal chest pain radiating to left jaw, cardiogenic shock"),
            Patient(id="d0000001-0000-0000-0000-000000000003", phc_id=phc1.id if phc1 else None, name="Kiran Vijay Mhatre", age=29, gender="Male", phone="+91-9988776657", blood_group="A+", emergency_summary="Polytrauma following highway collision, blunt abdominal trauma with suspected internal hemorrhage"),
        ]
        db.add_all(patients)
        db.commit()

    # 5. User Profiles
    if not db.query(Profile).count():
        logger.info("Seeding demo user accounts...")
        phc1 = db.query(PHC).first()
        hosp1 = db.query(Hospital).first()
        profiles = [
            Profile(id="e0000001-0000-0000-0000-000000000001", name="Dr. Priya Sharma (PHC Medical Officer)", email="doctor@demo.com", password_hash=hash_password("demo123"), role="PHC", phone="+91-9000000001", organization_id=phc1.id if phc1 else None),
            Profile(id="e0000001-0000-0000-0000-000000000002", name="Dr. Arvind Deshmukh (Hospital Admin)", email="hospital@demo.com", password_hash=hash_password("demo123"), role="HOSPITAL", phone="+91-9000000002", organization_id=hosp1.id if hosp1 else None),
            Profile(id="e0000001-0000-0000-0000-000000000003", name="System Administrator", email="admin@demo.com", password_hash=hash_password("demo123"), role="ADMIN", phone="+91-9000000000", organization_id=None),
            Profile(id="e0000001-0000-0000-0000-000000000004", name="Demo Patient", email="patient@demo.com", password_hash=hash_password("demo123"), role="PATIENT", phone="+91-9988776655", organization_id=None)
        ]
        db.add_all(profiles)
        db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize tables and seed database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    logger.info(f"{settings.APP_NAME} started successfully.")
    yield
    logger.info(f"{settings.APP_NAME} shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Full-stack Rural Emergency Hospital Referral & Ambulance Coordination Platform",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "live_backend"
    }

@app.get("/", include_in_schema=False)
def root():
    return {"message": "RuralRefLink Emergency Coordination API is running. Visit /docs for OpenAPI documentation."}
