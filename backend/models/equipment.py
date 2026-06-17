from pydantic import BaseModel

class EquipmentCreate(BaseModel):
    equipment_name: str
    equipment_type: str

    manufacturer: str | None = None
    power_kw: float | None = None
    capex_eur: float | None = None
    throughput: float | None = None