from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional

from app.services.auth0_service import verify_jwt
from app.services.gemini_service import simulate_agent, list_available_agents
from app.models.schemas import AgentSimulationRequest, AgentSimulationResponse, Agent

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/", response_model=List[Agent])
async def get_available_agents(current_user: dict = Depends(verify_jwt)):
    """
    List all available AI agents for simulation
    """
    return await list_available_agents()

@router.post("/simulate", response_model=AgentSimulationResponse)
async def run_agent_simulation(
    simulation: AgentSimulationRequest = Body(...),
    current_user: dict = Depends(verify_jwt)
):
    """
    Run a simulation with a specified agent
    """
    try:
        result = await simulate_agent(
            agent_id=simulation.agent_id,
            parameters=simulation.parameters,
            datasets=simulation.datasets
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )