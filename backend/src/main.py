from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import redis
import pusher

import random, string

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins = ["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

rds = redis.Redis(host='redis-10873.c44.us-east-1-2.ec2.redns.redis-cloud.com', port=10873, password='qFhyU0rV9a75D9jJCq5NjN7sZvM7jyuT', decode_responses=True)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_name: str) -> None:
        await websocket.accept()
        self.active_connections[client_name] = websocket

    def disconnect(self, client_name: str) -> None:
        print("接続を切るものを確認", self.active_connections)
        self.active_connections.pop(client_name)

    async def send_personal_message(self, message: str, client_name: str) -> None:
        await self.active_connections[client_name].send_text(message)

    # async def broadcast(self, room_id: str) -> None:
    #     for connection in self.active_connections:
    #         await connection.send_text(message)
    
    async def multicast(self, room_id: str, client_name: str, message: str) -> None:
      room_list = rds.lrange(room_id, 0, -1)
      for name in room_list:
        await self.active_connections[name].send_json({"user_name":client_name, "message":message})
    
    async def create_room(self, room_id: str, host_name) -> None:
      print(room_id)
      rds.rpush(room_id, host_name)
      print("作成終了")

    async def delete_room(self, room_id):
      self.active_room.pop(room_id)
    
    async def entry(self, room_id: str, client_name: str) -> None:
      rds.rpush(room_id, client_name)

    async def exit(self, room_id:str, client_name: str):
      self.disconnect(client_name)
      rds.lrem(room_id, 1, client_name)
      await self.multicast(room_id, "Game Master", f"{client_name}が退出しました")

manager = ConnectionManager()

@app.websocket("/ws/{client_name}/room/{room_id}")
async def websocket_endpoint(websocket: WebSocket, client_name: str, room_id: str):
    await manager.connect(websocket, client_name)
    print("通信成功")
    print("どのユーザーが接続しているかの確認",manager.active_connections)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_name} says: {data}")
    except:
        await manager.exit(room_id, client_name)

class User(BaseModel):
  user_name: str

@app.post("/create_room")
async def create_room(user:User):
  randlst = [random.choice(string.ascii_letters + string.digits) for i in range(6)]
  room_id = ''.join(randlst)
  try:
    await manager.create_room(room_id, user.user_name)
    return {"room_id":room_id}
  except:
    return {"error":"ルーム作成に失敗しました"}

class Entry(BaseModel):
  user_name: str
  room_id: str

@app.post("/entry")
async def entry(entry:Entry):
  await manager.entry(entry.room_id, entry.user_name)
  return {"success":"部屋に入ります"}

class Msg(BaseModel):
  user_name: str
  room_id: str
  message: str

@app.post("/msg")
async def send_message(msg:Msg):
  await manager.multicast(msg.room_id, msg.user_name, msg.message)
  return 0

@app.post("/redis_get")
async def redis_get(entry:Entry):
    key = entry.room_id
    json_str = rds.lrange(key,0,-1)
    return json_str

pusher_client = pusher.Pusher(
  app_id='1795315',
  key='9dc8aa0916d5d9e98e44',
  secret='6de53ba1c4326cf250b2',
  cluster='ap3',
  ssl=True
)

pusher_client.trigger('my-channel', 'my-event', {'message': 'hello world'})
