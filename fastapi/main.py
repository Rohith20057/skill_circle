from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from database.database import client
from models import UserRegister, UserLogin, ContactMessage
from pymongo.errors import ServerSelectionTimeoutError

app = FastAPI(title="SkillCircle API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use database from the MongoDB client
db = client.get_database("skillcircle")
users_collection = db["users"]
contacts_collection = db["contacts"]

# In-memory fallback if MongoDB Atlas is blocking the IP
fallback_users = []
fallback_contacts = []

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    try:
        # Attempt MongoDB
        existing_user = users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_dict = user.model_dump()
        users_collection.insert_one(user_dict)
        
        return {"message": "User registered successfully"}
    except ServerSelectionTimeoutError:
        # FALLBACK: Store in local memory
        print("MongoDB timed out. Using local memory fallback for registration.")
        if any(u["email"] == user.email for u in fallback_users):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        fallback_users.append(user.model_dump())
        return {"message": "User registered successfully (Local Mode)"}

@app.post("/api/login")
async def login_user(user: UserLogin):
    try:
        # Attempt MongoDB
        existing_user = users_collection.find_one({"email": user.email})
        
        if not existing_user or existing_user["password"] != user.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        return {"message": "Login successful", "user": {"email": existing_user["email"], "fullname": existing_user["fullname"]}}
    except ServerSelectionTimeoutError:
        # FALLBACK: Check local memory
        print("MongoDB timed out. Using local memory fallback for login.")
        existing_fallback = next((u for u in fallback_users if u["email"] == user.email), None)
        
        if not existing_fallback or existing_fallback["password"] != user.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        return {"message": "Login successful (Local Mode)", "user": {"email": existing_fallback["email"], "fullname": existing_fallback["fullname"]}}

@app.post("/api/contact", status_code=status.HTTP_201_CREATED)
async def submit_contact(contact: ContactMessage):
    try:
        contact_dict = contact.model_dump()
        contacts_collection.insert_one(contact_dict)
        return {"message": "Feedback submitted successfully"}
    except ServerSelectionTimeoutError:
        fallback_contacts.append(contact.model_dump())
        return {"message": "Feedback submitted successfully (Local Mode)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
