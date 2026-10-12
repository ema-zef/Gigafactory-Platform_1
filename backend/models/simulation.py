from typing import Literal
from pydantic import BaseModel, Field

class RouteStep(BaseModel):
    execution_mode: Literal["in_house", "outsourced", "purchased_intermediate"] = "in_house"
    technology_id: int | None = None
    technology_name: str = ""
    process: str = ""
    process_category: str = ""
    quality_rate: float = Field(default=100, gt=0, le=100)
    fee_eur_per_unit: float = Field(default=0, ge=0)
    transport_eur_per_unit: float = Field(default=0, ge=0)
    emissions_kgco2e_per_unit: float = Field(default=0, ge=0)
    input_material: str | None = None
    # Purchased intermediates use a boundary unit: kg, m, or cells.
    # Outsourced steps use the category-derived processing unit.
    environment: Literal[
        "none",
        "dry_room",
        "glove_box",
        "mini_environment",
    ] = "none"

class SimulationRequest(BaseModel):
    plant_code: str
    product_code: str
    plant_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    product_material_id: int | None = Field(default=None, gt=0)
    cathode_route: list[RouteStep] = Field(default_factory=list)
    anode_route: list[RouteStep] = Field(default_factory=list)
    assembly_route: list[RouteStep] = Field(default_factory=list)
