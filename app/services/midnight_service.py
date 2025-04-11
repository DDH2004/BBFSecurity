from midnight import Midnight

class MidnightService:
    def __init__(self, api_key: str):
        self.midnight = Midnight(api_key)

    def protect_data(self, data: dict) -> dict:
        return self.midnight.protect(data)

    def grant_access(self, user_id: str, resource_id: str) -> bool:
        return self.midnight.grant_access(user_id, resource_id)

    def revoke_access(self, user_id: str, resource_id: str) -> bool:
        return self.midnight.revoke_access(user_id, resource_id)

    def check_access(self, user_id: str, resource_id: str) -> bool:
        return self.midnight.check_access(user_id, resource_id)