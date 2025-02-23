from fastapi import FastAPI
from auth import router as auth_router
from referral_system import router as referral_router
import uvicorn



app = FastAPI()

app.include_router(auth_router, tags=['jwt authorization system'])
app.include_router(referral_router, tags=['referral system'])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=80,
        reload=True
    )
