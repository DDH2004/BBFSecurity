from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import agents, data, auth
from app.core.config import settings
from app.middleware.security_middleware import add_security_middleware
from app.services.mongodb_service import connect_to_mongodb, close_mongodb_connection

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
add_security_middleware(app)

# Include API routes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(data.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongodb_connection()

@app.get("/")
def root():
    return {"message": "Welcome to the AI Agent Simulation System"}