from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from auth import User, SessionDept, oauth2_scheme, check_user, decode_token
from models import UserModel, ReferralCodeModel
from sqlalchemy.ext.asyncio import AsyncSession
from  typing import Annotated
from password_security import hash_password
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import selectinload


router = APIRouter()




SECRET_KEY = '2nXGNMkA_wye3VgbduZtd1YvttLXUrOF4p-qYxQr4lY='
ALGORITHM = 'HS256'
CODE_LIFETIME_DAYS = 10 




def create_referral_code(payload: dict):
    code = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return code




async def check_referrer(owner_id: int, db: SessionDept):

    query = select(ReferralCodeModel).where(ReferralCodeModel.owner_id==owner_id)
    referral_code_model_object = await db.execute(query)

    return referral_code_model_object.scalar_one_or_none()




async def decode_referral_code(code: str, db: SessionDept):
        

        try:
            payload = jwt.decode(code, SECRET_KEY, ALGORITHM)

            owner_id = int(payload.get('sub'))
            type_code = payload.get('type')


            if owner_id is None:
                return None
            
            if type_code != 'referral':
                return None
            

            referral_code_model_object = await check_referrer(owner_id=owner_id, db=db)

            if referral_code_model_object is None:
                return None

            user_object = await db.get(UserModel, referral_code_model_object.owner_id)
        
            
        except JWTError as exept: 
            return None

        return user_object




async def registration_by_referral(user: User, referral_code: str, db: SessionDept):

    user_object = await check_user(email=user.email, db=db)

    if user_object:
        return None
    
    user_referrer_object = await decode_referral_code(code=referral_code, db=db)
    
    
    if user_referrer_object is None:

        return None
    

    try:   
        hashed_password = hash_password(user.password)
        db.add(UserModel(
            email=user.email,
            password=hashed_password,
            referred_by = user_referrer_object.id
        ))

        await db.commit()
    except Exception as exept:
        return None

    return True


@router.post('/registration_like_referral')
async def referral_register(user: User, referral_code: str, db: SessionDept):

    referral_register_object = await registration_by_referral(user=user, referral_code=referral_code, db=db)

    if referral_register_object is None:
        return {'Message': 'Invalid data'}

    return {'Message': 'You have been registered successfully'}



@router.post('/create_my_referral_code')
async def create_my_code(me: Annotated[str, Depends(decode_token)], db: SessionDept):
    
    user_object = str(me.id)

    if me.referral_code:
        return {"Message:" "Код уже существует"}
    code_lifetime = datetime.now(timezone.utc) + timedelta(days=CODE_LIFETIME_DAYS)
    
    payload = {'sub': user_object, 'exp': code_lifetime, 'type': 'referral'}

    new_code = create_referral_code(payload=payload)

    try:
        me.referral_code = new_code

        db.add(ReferralCodeModel(
            code=new_code,
            user=me
        ))

        await db.commit()

    except Exception as exept:
        return {"Message:" "Error"}
    
    return {"Referral_code": new_code}

@router.get('/get_referrals/{user_id}')
async def get_referrals(user_id: int, db: SessionDept):

    query = select(UserModel).where(UserModel.id == user_id).options(selectinload(UserModel.referrals))

    result = await db.execute(query)  
        
    user_object = result.scalar()     
    
    return {"Referrers": user_object.referrals}



@router.get("/get_code_by_email/{email}")
async def get_referrer(email: str, db: SessionDept):

    query = select(UserModel).where(UserModel.email==email)

    referrer_code =  await db.execute(query)

    return {"Referral_code": referrer_code.scalar_one_or_none().referral_code}






    





