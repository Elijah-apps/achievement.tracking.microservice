from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Initialize FastAPI app
app = FastAPI()

# Model for a user
class User(BaseModel):
    id: int
    username: str

# Model for an achievement
class Achievement(BaseModel):
    id: int
    name: str
    description: str
    points: int
    earned_date: datetime

# Model to track the achievement status of a user
class UserAchievement(BaseModel):
    user_id: int
    achievement_id: int
    achieved: bool
    date_achieved: datetime = None

# Simulating databases
users_db = []
achievements_db = []
user_achievements_db = []

# Route to register a user
@app.post("/api/register-user")
def register_user(user: User):
    if any(u.id == user.id for u in users_db):
        raise HTTPException(status_code=400, detail="User already exists")
    
    users_db.append(user)
    return {"message": f"User {user.username} registered successfully!"}

# Route to get all users
@app.get("/api/users", response_model=List[User])
def get_users():
    if not users_db:
        raise HTTPException(status_code=404, detail="No users found")
    return users_db

# Route to add a new achievement
@app.post("/api/add-achievement")
def add_achievement(achievement: Achievement):
    if any(a.id == achievement.id for a in achievements_db):
        raise HTTPException(status_code=400, detail="Achievement already exists")
    
    achievements_db.append(achievement)
    return {"message": f"Achievement '{achievement.name}' added successfully!"}

# Route to get all achievements
@app.get("/api/achievements", response_model=List[Achievement])
def get_achievements():
    if not achievements_db:
        raise HTTPException(status_code=404, detail="No achievements found")
    return achievements_db

# Route to track user achievements
@app.post("/api/earn-achievement")
def earn_achievement(user_id: int, achievement_id: int):
    # Check if the user exists
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the achievement exists
    achievement = next((a for a in achievements_db if a.id == achievement_id), None)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    # Check if the user has already earned the achievement
    existing_user_achievement = next((ua for ua in user_achievements_db if ua.user_id == user_id and ua.achievement_id == achievement_id), None)
    if existing_user_achievement:
        raise HTTPException(status_code=400, detail="User already earned this achievement")
    
    # Add the achievement to the user's record
    user_achievement = UserAchievement(
        user_id=user_id,
        achievement_id=achievement_id,
        achieved=True,
        date_achieved=datetime.now()
    )
    user_achievements_db.append(user_achievement)

    return {"message": f"User {user.username} earned achievement '{achievement.name}'!"}

# Route to get all achievements earned by a user
@app.get("/api/user-achievements/{user_id}", response_model=List[UserAchievement])
def get_user_achievements(user_id: int):
    # Get all earned achievements for the user
    user_achievements = [ua for ua in user_achievements_db if ua.user_id == user_id]
    if not user_achievements:
        raise HTTPException(status_code=404, detail="No achievements found for this user")
    
    return user_achievements

# Route to get the status of a specific achievement for a user
@app.get("/api/user-achievement-status/{user_id}/{achievement_id}")
def get_user_achievement_status(user_id: int, achievement_id: int):
    # Check if the user has earned the achievement
    user_achievement = next((ua for ua in user_achievements_db if ua.user_id == user_id and ua.achievement_id == achievement_id), None)
    if not user_achievement:
        raise HTTPException(status_code=404, detail="Achievement not earned by user")
    
    return {"user_id": user_id, "achievement_id": achievement_id, "earned": user_achievement.achieved, "date_achieved": user_achievement.date_achieved}

# Route to reset an achievement (for example, if the achievement is revocable)
@app.post("/api/reset-achievement")
def reset_achievement(user_id: int, achievement_id: int):
    # Find the user's achievement record
    user_achievement = next((ua for ua in user_achievements_db if ua.user_id == user_id and ua.achievement_id == achievement_id), None)
    if not user_achievement:
        raise HTTPException(status_code=404, detail="User achievement record not found")

    # Reset achievement status
    user_achievement.achieved = False
    user_achievement.date_achieved = None

    return {"message": f"Achievement {achievement_id} has been reset for user {user_id}."}

# Root route with a welcome message
@app.get("/")
def read_root():
    return {"message": "Welcome to the Achievement Tracking Microservice!"}

# Run the app using uvicorn (this can be done directly or using the command line)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
