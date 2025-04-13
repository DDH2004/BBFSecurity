# dev_token.py
import jwt, time
token = jwt.encode(
    {"sub": "agent1", "exp": int(time.time()) + 3600},
    "dev-secret",
    algorithm="HS256"
)
print(token)
