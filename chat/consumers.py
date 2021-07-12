import json
from os import name
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import date, datetime
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from chat.models import Chat, Group

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # print(self.scope)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        print("Connecting...")
        await self.accept()

        # Send previous chat messages on connect
        await self.send(text_data=json.dumps({
            "chat" : await self.get_previous_chats(self.room_name)
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print("Text data is", text_data)
        text_data_json = json.loads(text_data)
        date = str(datetime.now())
        message = text_data_json['message']
        user = str(self.scope["user"])
        group = self.room_name
        chat = [
                {
                    "user" : user,
                    "message" : message,
                    "date" : date,
                },
            ]

        await self.save_chat(user = user, group = group, message = message, date = date)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                "chat" : json.dumps(chat),
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        chat = event["chat"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "chat" : chat
        }))

    @database_sync_to_async
    def get_previous_chats(self, group):
        group_id = Group.objects.filter(name = group)[0]
        chat_query = Chat.objects.filter(group_id = group_id)
        chats = list(chat_query.values())
        for chat in chats:
            chat["date"] = str(chat["date"])
            chat["user_id"] = str(User.objects.filter(id = chat["user_id"])[0])
        return json.dumps(chats)

    @database_sync_to_async
    def save_chat(self, user, group, message, date):
        user_id = User.objects.filter(username = user)[0].id
        group_id = Group.objects.filter(name = group)[0].id
        chat_save = Chat(user_id = user_id, group_id = group_id, date = date, message = message)
        chat_save.save()
        