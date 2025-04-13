"""
dbTest.py
Quick sanity check for agent_model helpers.
Run with:  python3 dbTest.py
"""

from pprint import pprint
from db.agent_model import add_agent, get_agent, update_contract

# 1) Add (or re‑add) an agent.
try:
    agent_id = "agent1"
    seed = "22c182383f2e79a055a0ea6ece378d16d9b9cc5f53855688f06e43d3e74e1777"
    contract_hex = "020044c4088f5de99dc9267a0ce100748120592c8badc7dbee728de1a4cd1e5e9ee8"

    inserted_id = add_agent(agent_id, seed, contract_hex)
    print(f"✅ Inserted new agent with _id={inserted_id}")
except ValueError as e:
    print(f"⚠️  {e} (already exists)")

# 2) Fetch the agent we just added.
agent = get_agent("agent1")
print("\n🔍 get_agent('agent1') returned:")
pprint(agent)

# 3) Update contract hex for that agent.
new_hex = "deadbeef00aa55cc..."  # dummy example
if update_contract("agent1", new_hex):
    print("\n✅ Contract updated.")
else:
    print("\n❌ Contract update failed.")

# 4) Verify the update.
agent_after = get_agent("agent1")
print("\n🔍 Agent after update:")
pprint(agent_after)
