from fastapi import FastAPI, HTTPException, Form
from DB.connect import DB_connection

app = FastAPI()

db = DB_connection()
session = db.sessionmaker()

@app.get("/")
async def root():
    return {"message": "Hi"}


