import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

MONGO_URL = os.getenv("MONGO_URL", "mongodb://db:27017")
DB_NAME = "fastapi_db"
COLLECTION_NAME = "humans"

class Human(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class HumanResponse(Human):
    id: str

MILK_COLLECTION = "milk"

class Milk(BaseModel):
    name: str
    price: float
    fat: float

class MilkResponse(Milk):
    id: str

client: AsyncIOMotorClient = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    print(f"Connected to MongoDB at {MONGO_URL}")
    yield
    if client:
        client.close()
        print("MongoDB connection closed")

app = FastAPI(
    title="Hello API with NoSQL",
    lifespan=lifespan
)

@app.post("/humans/create", response_model=HumanResponse)
async def create_human(human: Human):
    collection = db[COLLECTION_NAME]
    result = await collection.insert_one(human.model_dump())
    created_human = await collection.find_one({"_id": result.inserted_id})
    created_human["id"] = str(created_human.pop("_id"))
    return created_human

@app.get("/humans/", response_model=List[HumanResponse])
async def read_humans():
    collection = db[COLLECTION_NAME]
    humans = []
    async for human in collection.find():
        humans["id"] = str(human.pop("_id"))
        humans.append(human)
    return humans

@app.put("/humans/{human_id}", response_model=HumanResponse)
async def update_human(human_id: str, human: Human):
    try:
        obj_id = ObjectId(human_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid human ID format")
    
    collection = db[COLLECTION_NAME]
    existing = await collection.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Human not found")
    
    await collection.update_one(
        {"_id": obj_id},
        {"$set": human.model_dump()}
    )
    
    updated = await collection.find_one({"_id": obj_id})
    updated["id"] = str(updated.pop("_id"))
    return updated

@app.delete("/humans/{human_id}", response_model=HumanResponse)
async def delete_human(human_id: str = Path(..., description="MongoDB ObjectId")):
    collection = db[COLLECTION_NAME]
    
    result = await collection.delete_one({"_id": ObjectId(human_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Human not found")
    return HumanResponse(id=human_id, name="", price=0.0)

@app.post("/milk/create", response_model=MilkResponse)
async def create_milk(human: Milk):
    collection = db[MILK_COLLECTION]
    result = await collection.insert_one(human.model_dump())
    created_human = await collection.find_one({"_id": result.inserted_id})
    created_human["id"] = str(created_human.pop("_id"))
    return created_human

@app.get("/humans/", response_model=List[HumanResponse])
async def read_humans():
    collection = db[COLLECTION_NAME]
    humans = []
    async for human in collection.find():
        human["id"] = str(human.pop("_id"))
        humans.append(human)
    return humans

@app.put("/humans/{human_id}", response_model=HumanResponse)
async def update_human(human_id: str, human: Human):
    try:
        obj_id = ObjectId(human_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid human ID format")
    
    collection = db[COLLECTION_NAME]
    existing = await collection.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Human not found")
    
    await collection.update_one(
        {"_id": obj_id},
        {"$set": human.model_dump()}
    )
    
    updated = await collection.find_one({"_id": obj_id})
    updated["id"] = str(updated.pop("_id"))
    return updated

@app.delete("/humans/{human_id}", response_model=HumanResponse)
async def delete_human(human_id: str = Path(..., description="MongoDB ObjectId")):
    collection = db[COLLECTION_NAME]
    
    result = await collection.delete_one({"_id": ObjectId(human_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Human not found")
    return HumanResponse(id=human_id, name="", price=0.0)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI + MongoDB"}
