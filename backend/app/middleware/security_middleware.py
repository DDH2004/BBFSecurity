from fastapi import FastAPI, Request, Response
from app.core.config import settings
from app.services.midnight_service import midnight_service

async def midnight_security_middleware(request: Request, call_next):
    """
    Middleware to apply Midnight security layer between the API and MongoDB
    """
    # Handle the midnight-disable header to toggle security
    midnight_disabled = request.headers.get("midnight-disable", "").lower() == "true"
    if midnight_disabled:
        midnight_service.set_enabled(False)
    else:
        midnight_service.set_enabled(True)
    
    # Extract user ID if available from authorization
    user_id = "anonymous"
    auth_header = request.headers.get("authorization")
    if (auth_header and auth_header.startswith("Bearer ")):
        # In a real implementation, you'd extract and validate the user ID
        # For now, we're setting a placeholder
        user_id = "authenticated-user"
    
    # Determine resource and action from the request
    path = request.url.path
    method = request.method
    
    # Simplified resource type detection based on URL path
    resource_type = "unknown"
    resource_id = None
    
    if "/data/" in path:
        resource_type = "dataset"
        # Extract ID from path if present
        parts = path.split("/")
        if len(parts) > 3 and parts[3]:
            resource_id = parts[3]
    elif "/agents/" in path:
        resource_type = "agent"
        # Extract ID from path if present
        parts = path.split("/")
        if len(parts) > 3 and parts[3]:
            resource_id = parts[3]
    
    # Map HTTP method to action
    action_map = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "DELETE": "delete"
    }
    action = action_map.get(method, "unknown")
    
    # Verify access through Midnight
    has_access = await midnight_service.verify_access(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action
    )
    
    if not has_access:
        return Response(
            content='{"detail":"Access denied"}',
            status_code=403,
            media_type="application/json"
        )
    
    # Log the access attempt
    await midnight_service.audit_log(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details={"path": path, "method": method}
    )
    
    # Process the request
    response = await call_next(request)
    
    # In a complete implementation, you might want to process the response data
    # through Midnight's security layer as well
    
    return response

def add_security_middleware(app: FastAPI):
    """
    Add the security middleware to the FastAPI app
    """
    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        return await midnight_security_middleware(request, call_next)