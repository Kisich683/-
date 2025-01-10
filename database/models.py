from sqlalchemy import String, BigInteger, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id = mapped_column(BigInteger, unique=True)
    chat_id = mapped_column(BigInteger)
    nick_name: Mapped[str] = mapped_column(String(50), nullable=False)
    come_time: Mapped[str] = mapped_column(String(10), nullable=True)
    leave_time: Mapped[str] = mapped_column(String(10), nullable=True)
    in_game: Mapped[bool] = mapped_column(Boolean)
