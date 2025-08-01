from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from enum import Enum

class TypeProgram(Enum):
    OneC = "OneC"
    Telegram = "Telegram"
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[str] = mapped_column(String, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email:Mapped[str] = mapped_column(String, nullable=True)


class Program(Base):
    __tablename__ = 'programs'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    program_uid: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    clienttype: Mapped[TypeProgram] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    # Связь с ConnectionSetting
    connection_settings: Mapped["ConnectionSetting"] = relationship(
        "ConnectionSetting", back_populates="program", cascade="all, delete-orphan"
    )

class ConnectionSetting(Base):
    __tablename__ = 'connection_settings'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    program_uid: Mapped[str] = mapped_column(String, ForeignKey("programs.program_uid"), nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    client_login: Mapped[str] = mapped_column(String, nullable=True)
    client_pass: Mapped[str] = mapped_column(String, nullable=True)
    endpoint: Mapped[str] = mapped_column(String, nullable=True)

    # Связь с Program
    program: Mapped[Program] = relationship("Program", back_populates="connection_settings") 