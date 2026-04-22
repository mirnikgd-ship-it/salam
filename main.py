import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

MONGO_URL = os.getenv("MONGO_URL", "mongodb://db:27017")
DB_NAME = "fastapi_db"
COLLECTION_NAME = "items"

class Item(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class ItemResponse(Item):
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

@app.post("/items/create", response_model=ItemResponse)
async def create_item(item: Item):
    collection = db[COLLECTION_NAME]
    result = await collection.insert_one(item.model_dump())
    created_item = await collection.find_one({"_id": result.inserted_id})
    created_item["id"] = str(created_item.pop("_id"))
    return created_item

@app.get("/items/", response_model=List[ItemResponse])
async def read_items():
    collection = db[COLLECTION_NAME]
    items = []
    async for item in collection.find():
        item["id"] = str(item.pop("_id"))
        items.append(item)
    return items

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item: Item):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    collection = db[COLLECTION_NAME]
    existing = await collection.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await collection.update_one(
        {"_id": obj_id},
        {"$set": item.model_dump()}
    )
    
    updated = await collection.find_one({"_id": obj_id})
    updated["id"] = str(updated.pop("_id"))
    return updated

@app.delete("/items/{item_id}", response_model=ItemResponse)
async def delete_item(item_id: str = Path(..., description="MongoDB ObjectId")):
    collection = db[COLLECTION_NAME]
    
    result = await collection.delete_one({"_id": ObjectId(item_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(id=item_id, name="", price=0.0)

@app.post("/milk/create", response_model=MilkResponse)
async def create_milk(item: Milk):
    collection = db[MILK_COLLECTION]
    result = await collection.insert_one(item.model_dump())
    created_item = await collection.find_one({"_id": result.inserted_id})
    created_item["id"] = str(created_item.pop("_id"))
    return created_item
#И так далее везде Item. items и т.д. меняем на milk
@app.get("/items/", response_model=List[ItemResponse])
async def read_items():
    collection = db[COLLECTION_NAME]
    items = []
    async for item in collection.find():
        item["id"] = str(item.pop("_id"))
        items.append(item)
    return items

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item: Item):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    collection = db[COLLECTION_NAME]
    existing = await collection.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await collection.update_one(
        {"_id": obj_id},
        {"$set": item.model_dump()}
    )
    
    updated = await collection.find_one({"_id": obj_id})
    updated["id"] = str(updated.pop("_id"))
    return updated

@app.delete("/items/{item_id}", response_model=ItemResponse)
async def delete_item(item_id: str = Path(..., description="MongoDB ObjectId")):
    collection = db[COLLECTION_NAME]
    
    result = await collection.delete_one({"_id": ObjectId(item_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(id=item_id, name="", price=0.0)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI + MongoDB"}
