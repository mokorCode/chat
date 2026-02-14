from fastapi import FastAPI
from requests import Request
import json
import uuid
from pydantic import BaseModel
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173", "https://cfb0-2409-8a20-2a95-ce94-5d16-8090-ea8a-185a.ngrok-free.app"],
    allow_origins=["http://localhost:5173", "https://abdd-2409-8a20-2a95-ce94-f9fe-c6f7-b47a-425a.ngrok-free.app","https://c180-2409-8a20-2a95-ce94-98dd-8ea1-dfd1-ec86.ngrok-free.app"],
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
    useruuid: uuid.UUID

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
def uuid_scope(scope):
    return uuid.uuid5(uuid.NAMESPACE_DNS, scope)

def get_uuid(content, scope='user'):
    return uuid.uuid5(uuid_scope(scope), content)  
def update_db():
    with open('db_user', 'a+', encoding='utf-8') as f:
        f.seek(0)
        while True:
            line = f.readline()
            if line == '':
                break
            line = line.split('=w=')
            username = line[0].strip()
            hashed_password = line[1].strip()
            useruuid = get_uuid(username)
            
            db[username] = User(username=username, hashed_password=hashed_password, useruuid=useruuid)
update_db()
print(db)

hash_password = PasswordHash(hashers=[Argon2()])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def verify_password(pwd, hashed_pwd):
    print(f"验证密码: {pwd} 的哈希 {hash_password.hash(pwd)} 是否对应 {hashed_pwd}")
    return hash_password.verify(pwd, hashed_pwd)

def generate_token(sub: str, exp: timedelta = timedelta(minutes=EXPIRE)):
    expire = datetime.now(timezone.utc) + exp
    token = jwt.encode({'sub': sub, 'exp': expire}, SECRET_KEY, ALORITHM)

    return token

@app.middleware('http')
async def router_detector(request: Request, call_next):
    update_db()
    response = await call_next(request)
    return response

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
    useruuid = get_uuid(username)
    register = User(username=username, hashed_password=hashed_password, useruuid=useruuid)
    db[register.username] = register
    print(f'''
\033[1;32m<< 注册了用户: \033[0;33m{register.username}\033[0m
\033[1;32m<< 哈希密码: \033[0;33m{register.hashed_password}\033[0m
    ''')
    token = generate_token(register.username)
    print(f'\033[1;32m<< 生成了Token: \033[0;33m{token}\033[0m')
    print('————————————————————————————')
    with open('db_user', 'a', encoding='utf-8') as f:
        f.write(f'{username}=w={hashed_password}\n')
    useruuid = get_uuid(username)
    with open(f'db_sessions/{useruuid}', 'a+') as f:
        pass
    return {'access_token': token, 'token_type': 'Bearer'}

def get_token(token: str = Depends(oauth2_scheme)):
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALORITHM], options={ 'verify_exp': True })
        return payload
    except ExpiredSignatureError:
        raise HTTPException(401, 'token 已经过期')
    except InvalidTokenError:
        raise HTTPException(401, '无效的Token')
    
if not '$public-chat' in db.keys():
    root(RegisterData(username='$public-chat', password='@mokor233'))


@app.post('/login')
def login(login_data: LoginData):
    username = login_data.username
    password = login_data.password
    print(f'/login - {username} 尝试登陆')
    if username not in db:
        print(f'/login - {username} 不存在: 且输入密码 {password}')
        raise HTTPException(401, '用户不存在')
    is_valid = verify_password(password, db[username].hashed_password)
    if not is_valid:
        print(f'/login - {username} 密码错误: 输入了密码 {password}')
        raise HTTPException(401, '密码错误')
   
    token = generate_token(username, timedelta(minutes=5))
    appendUserSession(username, '$public-session')

    return {'access_token': token, 'token_type': 'Bearer'}

@app.post('/token')
def token(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    username = payload['sub']
    if username in db:
        new_token = generate_token(username, timedelta(minutes=5))
        return {'access_token': new_token, 'token_type': 'Bearer'}


class Message(BaseModel):
    time: str
    fromUser: str
    id: int
    content: str
    type: str

class Session(BaseModel):
    id: uuid.UUID | None | str
    isRead: bool
    msgNum: int
    members: list[str]
    contents: list[Message]

    def to_dict(self):
        return {
            'id': str(self.id),
            'isRead': self.isRead,
            'msgNum': self.msgNum,
            'members': self.members,
            'contents': [
                {
                    'time': msg.time,
                    'fromUser': msg.fromUser,
                    'id': msg.id,
                    'content': msg.content,
                    'type': msg.type
                } for msg in self.contents
            ]
        }



def read_sessions(username): # 读取会话
    useruuid = get_uuid(username)
    with open(f'db_sessions/{useruuid}', 'a+', encoding='utf-8') as f: # 会话文件在用户注册时创建 但是以防万一用a+模式打开以防止文件不存在
      return json.load(f)
    

    
@app.post('/me')
def me(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    username = payload['sub']
    try:
        sessions = read_sessions(username)
    except:
        sessions = {
            'username': username,
            'sessions': []
        }
    return {
        'username': username,
        'sessions': sessions
    }

@app.post('/users')
def users(token: str = Depends(oauth2_scheme)):
    verify_token(token)
    users = []
    with open('db_user', 'a+', encoding='utf-8') as f: # 这玩意也用a+嘛, 好
        f.seek(0)
        while True:
            line = f.readline()
            if not line:
                break
            line = line.split('=w=')
            username = line[0]
            users.append(username)
    return users

def appendUserSession(username, sessionId):
    useruuid = get_uuid(username)
    with open(f'db_sessions/{useruuid}', 'a+', encoding='utf-8') as f:
        f.seek(0)
        try:
            sessions = json.load(f)
        except:
            sessions = {
                'username': username,
                'sessions': []
            }
        if (username in sessions['sessions']):
            return
        sessions['sessions'].append(str(sessionId))
        with open(f'db_sessions/{useruuid}', 'w+', encoding='utf-8') as p:
            json.dump(sessions, p, ensure_ascii=False, indent=3)


def createSession(from_id, to_id) -> uuid.UUID:
    user_list = sorted([from_id, to_id])
    session_id = get_uuid('-'.join(user_list), 'session')
    session = Session(
        id= session_id,
        members=[from_id, to_id],
        isRead=True,
        msgNum=0,
        contents=[]
    )
    if (to_id == '$public-chat'):
        public_session_id = get_uuid('$public-session', 'session')
        session.members = ['$public']
        session.id = '$public-session'
        with open('./db_session/$public-session', 'w+', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=3)
        return public_session_id

    with open(f'./db_session/{session_id}', 'w+', encoding='utf-8') as f:
        json.dump(session.to_dict(), f, ensure_ascii=False, indent=3)
    appendUserSession(from_id, session_id)
    appendUserSession(to_id, session_id)
    return session_id

def read_session(from_id, to_id): # try-catch
    if (to_id == '$public-chat'):
        with open('./db_session/$public-session', 'r', encoding='utf-8') as f:
            public_contents = json.load(f)
            return public_contents

    user_list = sorted([from_id, to_id])
    session_id = get_uuid('-'.join(user_list), 'session')
    with open(f'./db_session/{session_id}', 'r', encoding='utf-8') as f: # 注意是r
        return json.load(f)

class GetSessionModel(BaseModel):
    checkFrom: str
    checkedFrom: str

@app.post('/get_session')
def get_session(data: GetSessionModel, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    checkFrom = data.checkFrom
    checkedFrom = data.checkedFrom
    username = payload['sub']
    if username != checkFrom:
        print('get_session-1')
        raise HTTPException(404, f'{username} - 访问会话时发起者与会话者不一致: 尝试查看 {checkFrom} 与 {checkedFrom} 的会话')
    if checkFrom not in db or checkedFrom not in db:
        print('get_session-2')
        raise HTTPException(404, f'{username} - 会话成员不存在: 尝试会话的 {checkFrom} 或 {checkedFrom} 账户不存在')
    try:
        session = read_session(username, checkedFrom)
        return session # 会话存在
    except: # 会话不存在，read json报错
        createSession(username, checkedFrom)
        session = read_session(username, checkedFrom)
        return session
    
class GetUpdateSession(BaseModel):
    session: Session

@app.post('/update_session') # 只能在一个地方使用，而那里提前进行了验证，因此这里不再使用token
def write_session(session: GetUpdateSession):
    session_now = session.session
    session_uuid = session_now.id
    with open(f'db_session/{session_uuid}', 'w+', encoding='utf-8') as f:
        json.dump(session_now.to_dict(), f, ensure_ascii=False, indent=3)
    return


    
        







    


if __name__ == "__main__":
    uvicorn.run('server:app', host='localhost', port=8000, reload=True)