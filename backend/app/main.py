from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .config import settings
from .routes import auth, documents, queries
from .middleware.error_handler import add_error_handlers

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A private AI-powered knowledge assistant with secure identity",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handlers
add_error_handlers(app)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(queries.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to the Private AI Assistant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)