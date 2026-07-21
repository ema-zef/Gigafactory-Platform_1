# models/simulation.py

from pydantic import BaseModel

class RouteStep(BaseModel):
    technology_id: int
    technology_name: str
    equipment_id: int | None = None
    
from pydantic import BaseModel

class RouteStep(BaseModel):
    technology_id: int
    technology_name: str
    equipment_id: int | None = None


class SimulationRequest(BaseModel):

    plant_code: str

    product_code: str

    cathode_route: list[RouteStep]

    anode_route: list[RouteStep]

    assembly_route: list[RouteStep]