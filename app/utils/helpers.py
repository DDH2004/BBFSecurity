def get_env_variable(var_name: str) -> str:
    import os
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' not found.")
    return value

def format_response(data: dict, status_code: int = 200) -> dict:
    return {
        "status": "success" if status_code < 400 else "error",
        "data": data,
        "status_code": status_code
    }

def log_request(request) -> None:
    import logging
    logging.info(f"Request: {request.method} {request.url} - Body: {request.body()}")