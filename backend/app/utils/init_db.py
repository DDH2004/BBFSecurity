# filepath: /workspaces/BBFSecurity/backend/app/utils/init_db.py
import asyncio
from app.services.mongodb_service import connect_to_mongodb, get_collection

async def init_db():
    await connect_to_mongodb()
    
    # Sample datasets
    datasets = await get_collection("datasets")
    if await datasets.count_documents({}) == 0:
        await datasets.insert_many([
            {
                "name": "Example Dataset 1",
                "description": "Sample dataset for testing",
                "sample_data": {"key1": "value1", "key2": "value2"},
                "tags": ["sample", "test"]
            },
            # Add more sample datasets
        ])
    
    print("Database initialized with sample data")

if __name__ == "__main__":
    asyncio.run(init_db())