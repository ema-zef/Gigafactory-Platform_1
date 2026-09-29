from fastapi import APIRouter, Depends
from auth import User, current_user
from models.simulation import SimulationRequest
from simulation.runner import run
router = APIRouter(tags=['simulation'])

@router.post('/simulation/run')
def run_simulation(request: SimulationRequest, user: User = Depends(current_user)):
    return {'status': 'success', 'result': run(request, user)}
