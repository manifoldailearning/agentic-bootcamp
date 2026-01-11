from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from zoneinfo import ZoneInfo
load_dotenv()
import uvicorn

app = FastAPI()

SECRET_KEY="super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

users = {
    "nachiketh": {"password": "nachiketh123", "role": "admin"},
    "rahul": {"password": "rahul123", "role": "user"},
}

def create_access_token(username: str, role: str):
    payload = {
        "sub": username, # subject
        "role": role, # role
        "exp": datetime.now(ZoneInfo("UTC")) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), # expiration time
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.post("/login")
def login(username: str, password: str): # backend authentication service
    user = users.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(username, user["role"]), "token_type": "bearer"} # return the access token

# @app.get("/user_info")
# def user_info(current_user: Depends(get_current_user)):
#     return {"message": "You are logged in", "user": current_user}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)