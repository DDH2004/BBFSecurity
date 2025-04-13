# app1.py  (or your main Flask file)
from flask import Flask, request, jsonify
from auth.token_utils import decode_oauth_token
from db.agent_model import get_agent
from midnight.cli_logger import log_access, get_counter_value   # ⬅️ new import

app = Flask(__name__)

# --- existing access route (unchanged) ------------------------------
@app.route("/access_data", methods=["POST"])
def access_data():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    agent_id = decode_oauth_token(token)
    if not agent_id:
        return jsonify({"error": "invalid_token"}), 401

    agent = get_agent(agent_id)
    if not agent:
        return jsonify({"error": "agent_not_found"}), 404

    # on‑chain log
    log_access(agent["wallet_seed"], agent["contract_hex"])
    return jsonify({"msg": f"Hello {agent_id}, access recorded on‑chain."})
# --------------------------------------------------------------------


# --- NEW: read‑only counter endpoint --------------------------------
@app.route("/usage_count", methods=["GET"])
def usage_count():
    """
    Returns the global counter value for the requesting agent’s contract.
    """
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    agent_id = decode_oauth_token(token)
    if not agent_id:
        return jsonify({"error": "invalid_token"}), 401

    agent = get_agent(agent_id)
    if not agent:
        return jsonify({"error": "agent_not_found"}), 404

    try:
        value = get_counter_value(agent["wallet_seed"], agent["contract_hex"])
        return jsonify({"counter": value})
    except Exception as e:
        app.logger.error(f"Counter read failed: {e}")
        return jsonify({"error": "counter_read_failed"}), 500
# --------------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=False)   # or port=5001, etc.
