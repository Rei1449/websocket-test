from datetime import datetime

from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from core.config import get_env

# Engine の作成
Engine = create_engine(
    get_env().database_url,
    encoding="utf-8",
    echo=False
)

BaseModel = declarative_base()


class Room(BaseModel):
  __tablename__ = 'rooms'
  id = Column(Integer, primary_key=True, autoincrement=True)
  room_id = Column(Integer, nullable=False)
  host_name = Column(String(50), nullable=False)
  player_one = Column(String(50), nullable=False)
  player_two = Column(String(50), nullable=False)
  player_three = Column(String(50), nullable=False)
