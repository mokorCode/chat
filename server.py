from fastapi import FastAPI
from pydantic import BaseModel
from jose import ExpiredSignatureError, JWTError
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)
class RegisterData(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    hashed_password: str

class LoginData(BaseModel):
    username: str
    password: str

# 准备好了吗， 要开始加密了
from fastapi import HTTPException, Depends
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import InvalidTokenError
from datetime import datetime, timedelta, timezone
from pwdlib.hashers.argon2 import Argon2Hasher as Argon2

SECRET_KEY = "TJ5Jp7Hj7aM-NLg2dCnmscXgW3RC9CkNONxuNYwAB0Ux4Oz0fPzR1s6L5Avk3DQgVb2E8dbo6uhxTresbAMM5w"
ALORITHM = "HS256"
EXPIRE = 5

db: dict[str, User] = {
}

hash_password = PasswordHash(hashers=[Argon2()])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def verify_password(pwd, hashed_pwd):
    print(f"验证密码: {pwd} 的哈希 {hash_password.hash(pwd)} 是否对应 {hashed_pwd}")
    return hash_password.verify(pwd, hashed_pwd)

def generate_token(sub: str, exp: timedelta = timedelta(minutes=EXPIRE)):
    expire = datetime.now(timezone.utc) + exp
    token = jwt.encode({'sub': sub, 'exp': expire}, SECRET_KEY, ALORITHM)

    return token


    

@app.post("/register")
def root(data: RegisterData):
    print('——————————注册请求——————————')
    username = data.username
    if username in db :
        print('<< 重复用户名注册')
        raise HTTPException(status_code=409, detail='账号已经存在')
    password = data.password
    if len(password) < 6:
        print('<< 过短的密码')
        raise HTTPException(status_code=409, detail='太短的密码')
    hashed_password = hash_password.hash(password)
    register = User(username=username, hashed_password=hashed_password)
    db[register.username] = register
    print(f'''
\033[1;32m<< 注册了用户: \033[0;33m{register.username}\033[0m
\033[1;32m<< 哈希密码: \033[0;33m{register.hashed_password}\033[0m
    ''')
    token = generate_token(register.username)
    print(f'\033[1;32m<< 生成了Token: \033[0;33m{token}\033[0m')
    print('————————————————————————————')
    return {'access_token': token, 'token_type': 'Bearer'}

def get_token(token: str = Depends(oauth2_scheme)):
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALORITHM], options={ 'verify_exp': True })
        return payload
    except ExpiredSignatureError:
        raise HTTPException(401, 'token 已经过期')
    except JWTError:
        raise HTTPException(401, '无效的Token')


@app.post('/login')
def login(login_data: LoginData):
    username = login_data.username
    password = login_data.password
    if username not in db:
        raise HTTPException(401, '用户不存在')
    is_valid = verify_password(password, db[username].hashed_password)
    if not is_valid:
        raise HTTPException(401, '密码错误')
    
    token = generate_token(username, timedelta(minutes=5))

    return {'access_token': token, 'token_type': 'Bearer'}

@app.post('/token')
def token(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    username = payload['sub']
    if username in db:
        new_token = generate_token(username, timedelta(minutes=5))
        return {'access_token': new_token, 'token_type': 'Bearer'}

    


    


if __name__ == "__main__":
    uvicorn.run('server:app', host='localhost', port=8000, reload=True)