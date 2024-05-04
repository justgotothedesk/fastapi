from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = FastAPI()

# 임시로 사용자 정보를 저장할 딕셔너리
users_db = {}

class User(BaseModel):
    name: str
    email: str
    password: str
    reset_key: str = None
    reset_limit_date: datetime = None

# 임시 User 데이터
users_db["test@example.com"] = User(name="Test User", email="test@example.com", password="temp")

class PasswordResetRequest(BaseModel):
    new_password: str


# 이메일 전송 함수
def send_email(recipient_email, subject, body):
    # 이메일 설정
    sender_email = "admin@example.com"  # 발신자 이메일 주소
    password = "admin_password"  # 발신자 이메일 비밀번호
    smtp_server = "smtp.example.com"  # SMTP 서버 주소

    # 이메일 내용 설정
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # 이메일 전송
    with smtplib.SMTP(smtp_server) as server:
        server.starttls()
        server.login(sender_email, password)
        server.send_message(message)


# 비밀번호 초기화 요청
@app.post("/reset-password-request")
async def reset_password_request(user: User):
    # 사용자 정보가 있는지 확인
    if user.email not in users_db or users_db[user.email].name != user.name:
        raise HTTPException(status_code=404, detail="User not found")

    # 비밀번호 리셋 키 생성 및 유효기간 설정
    reset_key = str(uuid.uuid4())
    reset_limit_date = datetime.now() + timedelta(days=1)

    # 사용자 정보에 비밀번호 리셋 키와 유효기간 저장
    users_db[user.email].reset_key = reset_key
    users_db[user.email].reset_limit_date = reset_limit_date

    # 비밀번호 리셋 이메일 전송
    subject = "Reset Your Password"
    body = f"Hi {user.name},\n\nPlease click the following link to reset your password: http://127.0.0.1:8000/reset-password?key={reset_key}\n\nThis link will expire in 24 hours."
    send_email(user.email, subject, body)

    # 이메일을 정상적으로 전달되었다고 프론트로 전달
    return {"message": 200}


# 비밀번호 초기화를 위한 리셋 키 확인
@app.post("/check-reset-key")
async def check_reset_key(request: PasswordResetRequest, reset_key: str = Form(...)):
    # 비밀번호 리셋 키 확인
    if reset_key not in [user.reset_key for user in users_db.values()]:
        raise HTTPException(status_code=400, detail="Invalid reset key")

    # 비밀번호 리셋 키의 유효기간 확인
    user_email = [email for email, user in users_db.items() if user.reset_key == reset_key][0]
    user = users_db[user_email]
    if user.reset_limit_date < datetime.now():
        raise HTTPException(status_code=400, detail="Reset key has expired")

    # 리셋 키가 유효하다고 전달
    return {"message": 200}

# 프론트로부터 받은 비밀번호로 변경
@app.post("/change-new-password")
async def change_new_password(new_password: str, user: User):
    users_db[user.email].password = new_password

    # 비밀번호가 정상적으로 초기화되었다고 전달
    return {"message": 200}