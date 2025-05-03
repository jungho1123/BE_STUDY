from fastapi import FastAPI
from pydantic import BaseModel

class UserSignupRequest(BaseModel):#회원가입
    username: str
    email: str
    password: str
     
class UserInDB(BaseModel): #회원가입 db로 저장
    id=int
    username:str
    hashed_password:str
    
class UserLoginRequest(BaseModel): #로그인요청
    username: str
    password: str

class TokenResponse(BaseModel): 
    access_token: str
    token_type: str = "bearer"  
    