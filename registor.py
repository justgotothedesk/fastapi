from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from reset_pwd import User, users_db
from passlib.context import CryptContext

app = FastAPI()

# 프론트로부터 받은 정보로 회원가입
@app.post("/registor-id")
async def registor_id(name: str, email: str, password: str):
    # 이메일이 존재하다면 오류 반환
    if email in users_db:
        return {"message": 404}
    
    bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    bcrypt_pwd = bcrypt_context.hash(password)
    
    users_db[email] = User(name=name, email=email, password=bcrypt_pwd)

    return {"message": 200}

