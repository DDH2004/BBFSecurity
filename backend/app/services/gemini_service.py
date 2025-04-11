import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json

from app.core.config import settings
from app.services.mongodb_service import store_agent_result

# Configure the Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

# Define available agent types
AVAILABLE_AGENTS = [
    {
        "id": "data-analyst",
        "name": "Data Analyst Agent",
        "description": "Analyzes datasets and provides insights"
    },
    {
        "id": "decision-maker",
        "name": "Decision Making Agent",
        "description": "Makes decisions based on provided criteria and data"
    },
    {
        "id": "communication",
        "name": "Communication Agent",
        "description": "Simulates communication between multiple agents"
    }
]

async def list_available_agents():
    """List all available agent types for simulation."""
    return AVAILABLE_AGENTS

async def simulate_agent(agent_id: str, parameters: Dict[str, Any], datasets: List[str] = None):
    """
    Run a simulation with the specified agent using Gemini API
    
    Args:
        agent_id: The type of agent to simulate
        parameters: Configuration parameters for the simulation
        datasets: List of dataset IDs to use in the simulation
    
    Returns:
        Simulation results
    """
    # Validate agent ID
    agent_exists = any(agent["id"] == agent_id for agent in AVAILABLE_AGENTS)
    if not agent_exists:
        raise ValueError(f"Agent type '{agent_id}' not found")
    
    # Get dataset information if provided
    dataset_info = []
    if datasets:
        from app.services.mongodb_service import get_dataset_by_id
        for dataset_id in datasets:
            data = await get_dataset_by_id(dataset_id)
            if data:
                dataset_info.append(data)
    
    # Construct prompt based on agent type and parameters
    prompt = construct_agent_prompt(agent_id, parameters, dataset_info)
    
    # Call Gemini API
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    
    # Process and structure the response
    try:
        # Try to extract structured data if the response is in JSON format
        result_text = response.text
        if result_text.startswith("```json") and result_text.endswith("```"):
            # Extract JSON content
            json_content = result_text.strip("```json").strip("```").strip()
            result_data = json.loads(json_content)
        else:
            # Use the raw text response
            result_data = {"response": result_text}
        
        # Store the simulation result
        result_id = await store_agent_result(agent_id, {
            "parameters": parameters,
            "datasets": datasets,
            "result": result_data
        })
        
        return {
            "agent_id": agent_id,
            "result_id": result_id,
            "data": result_data
        }
    except Exception as e:
        # Handle parsing errors
        return {
            "agent_id": agent_id,
            "error": str(e),
            "raw_response": response.text
        }

def construct_agent_prompt(agent_id: str, parameters: Dict[str, Any], dataset_info: List[Dict[str, Any]]):
    """
    Construct an appropriate prompt for the specified agent type
    """
    if agent_id == "data-analyst":
        return construct_data_analyst_prompt(parameters, dataset_info)
    elif agent_id == "decision-maker":
        return construct_decision_maker_prompt(parameters, dataset_info)
    elif agent_id == "communication":
        return construct_communication_prompt(parameters, dataset_info)
    else:
        return f"You are an AI agent of type {agent_id}. Please respond to the following parameters: {parameters}"

def construct_data_analyst_prompt(parameters, dataset_info):
    """Construct prompt for data analyst agent"""
    datasets_text = "\n\n".join([
        f"Dataset: {dataset.get('name', 'Unnamed')}\n"
        f"Description: {dataset.get('description', 'No description')}\n"
        f"Data: {dataset.get('sample_data', {})}"
        for dataset in dataset_info
    ])
    
    return f"""You are an AI data analyst. Analyze the following datasets and provide insights based on these parameters:
    
Analysis parameters: {parameters}

{datasets_text}

Provide your analysis in JSON format with these fields:
- insights: Array of key insights discovered
- correlations: Any correlations between data points
- recommendations: Actionable recommendations based on the data
- confidence: Your confidence level in the analysis (1-10)

Return your response as a JSON object enclosed in ```json ``` tags.
"""

def construct_decision_maker_prompt(parameters, dataset_info):
    """Construct prompt for decision maker agent"""
    datasets_text = "\n\n".join([
        f"Dataset: {dataset.get('name', 'Unnamed')}\n"
        f"Description: {dataset.get('description', 'No description')}\n"
        f"Data: {dataset.get('sample_data', {})}"
        for dataset in dataset_info
    ])
    
    criteria = parameters.get("criteria", "No specific criteria provided")
    options = parameters.get("options", [])
    options_text = "\n".join([f"- {option}" for option in options])
    
    return f"""You are an AI decision-making agent. Based on the following data and criteria, make a decision:
    
Decision criteria: {criteria}

Options to consider:
{options_text}

Available data:
{datasets_text}

Provide your decision in JSON format with these fields:
- decision: The selected option
- reasoning: Your step-by-step reasoning process
- alternatives: Ranked alternative options with brief explanations
- confidence: Your confidence level in the decision (1-10)
- risks: Potential risks associated with the decision

Return your response as a JSON object enclosed in ```json ``` tags.
"""

def construct_communication_prompt(parameters, dataset_info):
    """Construct prompt for communication simulation agent"""
    agents = parameters.get("agents", [])
    scenario = parameters.get("scenario", "General discussion")
    objective = parameters.get("objective", "Reach consensus")
    
    agents_text = "\n".join([
        f"- Agent {i+1}: {agent.get('name', f'Agent {i+1}')}, Role: {agent.get('role', 'Unspecified')}"
        for i, agent in enumerate(agents)
    ])
    
    return f"""You are a communication simulation agent. Simulate a conversation between multiple agents with the following scenario:
    
Scenario: {scenario}
Objective: {objective}

Participating agents:
{agents_text}

Simulate a realistic multi-turn conversation, with each agent responding based on their role and perspective.

Provide your simulation in JSON format with these fields:
- conversation: Array of messages with speaker and text
- outcome: Whether the objective was achieved
- key_points: Important points raised during the conversation
- analysis: Brief analysis of the communication dynamics

Return your response as a JSON object enclosed in ```json ``` tags.
"""