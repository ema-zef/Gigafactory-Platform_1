from pydantic import BaseModel, Field

class RouteStep(BaseModel):
    technology_id: int
    technology_name: str
    process: str
    process_category: str
    quality_rate: float

class SimulationRequest(BaseModel):
    plant_code: str
    product_code: str
    plant_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    product_material_id: int | None = Field(default=None, gt=0)
    cathode_route: list[RouteStep]
    anode_route: list[RouteStep]
    assembly_route: list[RouteStep]
