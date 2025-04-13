from db.agent_model import update_contract, _agents

_agents.update_one(
    {"agent_id": "agent1"},
    {"$set": {
        "wallet_seed": "22c182383f2e79a055a0ea6ece378d16d9b9cc5f53855688f06e43d3e74e1777"
    }}
)
