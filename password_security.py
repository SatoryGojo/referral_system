from passlib.context import CryptContext    

context = CryptContext(schemes=['bcrypt'])


def verify_password(password: str, hashed_password: str) -> str:
    return context.verify(password, hashed_password)

def hash_password(password: str) -> str:
    return context.hash(password)


