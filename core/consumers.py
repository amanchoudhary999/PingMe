import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from core.models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_id = room_id
        self.room_group_name = f"chat_{room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("✅ WS Connected:", room_id)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_text = data.get("message")

        if not msg_text:
            return

        msg_obj = await self.save_message(msg_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user": msg_obj["user"],
                "content": msg_obj["content"],
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "user": event["user"],
            "content": event["content"],
        }))

    @database_sync_to_async
    def save_message(self, content):
        user = self.scope["user"]
        room = Room.objects.get(id=self.room_id)

        msg = Message.objects.create(
            room=room,
            user=user,
            content=content
        )

        return {
            "user": user.name,
            "content": msg.content,
        }
