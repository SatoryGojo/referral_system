from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import ForeignKey, create_engine


class AbstractModel(DeclarativeBase):
    pass
    
class UserModel(AbstractModel):

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]

    referral_code: Mapped[str|None] = mapped_column(unique=True, default=None)

    
    referred_by: Mapped[int|None] = mapped_column(ForeignKey('users.id'), default=None, unique=False)

    
    referrals: Mapped[list["UserModel"]] = relationship("UserModel", remote_side=[referred_by], back_populates='referrer')      
    referrer: Mapped["UserModel"] = relationship("UserModel", remote_side=[id], back_populates="referrals")    


    referral_code_rel = relationship("ReferralCodeModel", back_populates="user", uselist=False)  



class ReferralCodeModel(AbstractModel):

    __tablename__ = "codes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    user = relationship("UserModel", back_populates="referral_code_rel")


engine = create_async_engine('postgresql+asyncpg://postgres:admin@localhost:5432/bdtestovoe')

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def db_connect():
    async with async_session() as db:
        yield db


# engine = create_engine('postgresql+psycopg2://postgres:admin@localhost:5432/bdtestovoe')


# AbstractModel.metadata.drop_all(engine)
# AbstractModel.metadata.create_all(engine)






