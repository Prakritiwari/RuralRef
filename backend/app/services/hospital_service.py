from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.hospital import Hospital
from ..models.resource import HospitalResource, Resource
from ..models.ambulance import Ambulance
from ..schemas.hospital import HospitalResponse
from ..schemas.resource import HospitalResourceResponse

def get_all_hospitals_summary(db: Session) -> List[HospitalResponse]:
    hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
    catalog_map = {r.id: r for r in db.query(Resource).all()}
    results = []

    for h in hospitals:
        invs = db.query(HospitalResource).filter(HospitalResource.hospital_id == h.id).all()
        avail_amb = db.query(Ambulance).filter(
            Ambulance.hospital_id == h.id,
            Ambulance.status == "AVAILABLE",
            Ambulance.is_active == True
        ).count()

        resource_dtos = []
        for inv in invs:
            res_meta = catalog_map.get(inv.resource_id)
            resource_dtos.append(
                HospitalResourceResponse(
                    id=inv.id,
                    hospital_id=inv.hospital_id,
                    resource_id=inv.resource_id,
                    resource_name=res_meta.name if res_meta else inv.resource_id,
                    resource_category=res_meta.category if res_meta else "GENERAL",
                    resource_unit=res_meta.unit if res_meta else "UNIT",
                    total_quantity=inv.total_quantity,
                    available_quantity=inv.available_quantity,
                    reserved_quantity=inv.reserved_quantity,
                    status=inv.status
                )
            )

        results.append(
            HospitalResponse(
                id=h.id,
                name=h.name,
                code=h.code,
                district=h.district,
                state=h.state,
                level=h.level,
                address=h.address,
                latitude=h.latitude,
                longitude=h.longitude,
                phone=h.phone,
                email=h.email,
                emergency_available=h.emergency_available,
                is_active=h.is_active,
                available_ambulances_count=avail_amb,
                resources=resource_dtos
            )
        )
    return results
