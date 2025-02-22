from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from models import db_connect, UserModel, ReferralCodeModel
from sqlalchemy import select
from password_security import verify_password, hash_password




router = APIRouter()
SessionDept = Annotated[AsyncSession, Depends(db_connect)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token') 

SECRET_KEY = '2nXGNMkA_wye3VgbduZtd1YvttLXUrOF4p-qYxQr4lY='
ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME_MINUTES = 10 
REFRESH_TOKEN_FIFETIME_DAYS = 7

    
class User(BaseModel):
    email: str
    password: str


async def check_user(email: str, db: SessionDept):
        query = select(UserModel).where(UserModel.email==email)
        user = await db.execute(query)
        return user.scalar_one_or_none()


async def registration(user: User, db: SessionDept):

    user_object = await check_user(email=user.email, db=db)

    if user_object:
        return None
    
    try:   
        hashed_password = hash_password(user.password)
        db.add(UserModel(
            email=user.email,
            password=hashed_password
        ))
        await db.commit()
    except Exception as exep:
        return None

    return True


async def authenticate(email: str, password: str, db: SessionDept):

    user_object = await check_user(email=email, db=db)

    if user_object is None:
        return None


    to_verify_password = user_object.password
    
    if not verify_password(password, to_verify_password):
        return None
    
    return user_object
    


def create_token(payload: dict):
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return token


async def decode_token(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDept):
        credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)
                                                    
        
        try:
            payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
            email = payload.get('sub')
            if email is None:
                raise credentials_exceptions
            
            user_object = await check_user(email=email, db=db)

            if user_object is None:
                raise credentials_exceptions
            
        except JWTError:    
            raise credentials_exceptions

        return user_object


@router.post('/registration')
async def register(user: User, db: SessionDept):

    registration_object = await registration(user=user, db=db)

    if registration_object is None:
        return {'Message': 'Invalid data'}

    return {'Message': 'You have been registered successfully'}

@router.post('/login')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDept):

   
    user_object = await authenticate(email=form_data.username, password=form_data.password, db=db)

    if user_object is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")


    # to_verify_password = user_object.hashed_password

    # print(to_verify_password)
    # if not verify_password(form_data.password, to_verify_password):
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    

    access_lifetime = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES) 
    payload = {'sub': form_data.username, 'exp':access_lifetime, 'type': 'access'}

    access_token = create_token(payload)

    refresh_lifetime = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_FIFETIME_DAYS) 
    payload = {'sub': form_data.username, 'exp': refresh_lifetime, 'type': 'refresh'}

    refresh_token = create_token(payload)


    return {"tokens":{
        "access_token": access_token,
        "refresh_token": refresh_token,
    }}


@router.post('/refresh')
async def refresh(refresh_token: str, db: SessionDept):

    refresh_except = HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Invalid refresh token"
        )
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, ALGORITHM)
        email = payload.get('sub')
        type_token = payload.get('type')

        if email is None or type_token != 'refresh':
            raise refresh_except
        
        user_object = await check_user(email=email, db=db)

        if user_object is None :
            raise refresh_except
        

    except JWTError:
        raise refresh_except
    
    new_access_lifetime = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
    new_payload = {'sub': email, 'exp': new_access_lifetime, 'type': 'access'}

    new_access_token = create_token(payload=new_payload)

    return {"tokens":{
        "access_token": new_access_token,
        "refresh_token": refresh_token,
    }}


@router.get('/users/me')
def my_page(me: Annotated[str, Depends(decode_token)]):
    return me
 