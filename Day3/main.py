from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import secrets
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

class UserRegister(BaseModel):
    username: str
    password: str

class MessageCreate(BaseModel):
    content: str



chat = FastAPI()

chat.mount("/static", StaticFiles(directory="static"), name="static")

@chat.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join("static", "index.html"), "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)



def get_db_connection():
    config = {
    'host': 'localhost',
    'user': 'root',  
    'password': '',  
    'database': 'simple_chat',
    'raise_on_warnings': True
}
    try:
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail="Database connection failed")
security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (credentials.username,))
    user = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if not user or not secrets.compare_digest(credentials.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

@chat.post("/register")
def register(user: UserRegister):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (user.username, user.password))
        connection.commit()
        return {"message": "User registered successfully"}
    except Error as e:
        connection.rollback()
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Username already exists")
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        cursor.close()
        connection.close()

@chat.get("/me")
def get_current_user_info(user: dict = Depends(get_current_user)):
    return {"username": user['username'], "user_id": user['id']}


@chat.get("/messages")
def get_all_messages():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """
        SELECT m.id, m.content, m.created_at, u.username 
        FROM messages m
        JOIN users u ON m.user_id = u.id
        ORDER BY m.created_at DESC
        """
        cursor.execute(query)
        messages = cursor.fetchall()
        return {"messages": messages}
    except Error as e:
        raise HTTPException(status_code=500, detail="Failed to fetch messages")
    finally:
        cursor.close()
        connection.close()


@chat.post("/messages")
def create_message(message: MessageCreate, user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        query = "INSERT INTO messages (user_id, content) VALUES (%s, %s)"
        cursor.execute(query, (user['id'], message.content))
        connection.commit()
        return {"message": "Message posted successfully"}
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Failed to post message")
    finally:
        cursor.close()
        connection.close()




from fastapi.middleware.cors import CORSMiddleware  

chat.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
uvicorn.run(chat, host="0.0.0.0", port=8002)