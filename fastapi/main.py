from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from database.database import client
from models import UserRegister, UserLogin, ContactMessage

app = FastAPI(title="SkillCircle API")

# Configure CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use database from the MongoDB client
db = client.get_database("skillcircle")
users_collection = db["users"]
contacts_collection = db["contacts"]

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Store user in database (password should ideally be hashed here)
    user_dict = user.model_dump()
    users_collection.insert_one(user_dict)
    
    return {"message": "User registered successfully"}

@app.post("/api/login")
async def login_user(user: UserLogin):
    # Find user
    existing_user = users_collection.find_one({"email": user.email})
    
    if not existing_user or existing_user["password"] != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return {"message": "Login successful", "user": {"email": existing_user["email"], "fullname": existing_user["fullname"]}}

@app.post("/api/contact", status_code=status.HTTP_201_CREATED)
async def submit_contact(contact: ContactMessage):
    contact_dict = contact.model_dump()
    contacts_collection.insert_one(contact_dict)
    return {"message": "Feedback submitted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
