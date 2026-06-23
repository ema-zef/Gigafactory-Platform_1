# models/simulation.py

from pydantic import BaseModel

class SimulationRequest(BaseModel):

    plant_code: str

    product_code: str

    target_output: float