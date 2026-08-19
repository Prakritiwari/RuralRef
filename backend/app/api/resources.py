from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.resource import Resource
from ..schemas.resource import ResourceCatalogResponse

router = APIRouter(prefix="", tags=["Resource Catalog"])

@router.get("/resources", response_model=List[ResourceCatalogResponse])
@router.get("/resources/catalog", response_model=List[ResourceCatalogResponse])
def get_resource_catalog(db: Session = Depends(get_db)):
    return db.query(Resource).filter(Resource.is_active == True).all()
