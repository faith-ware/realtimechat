import json
from os import name
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import date, datetime
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from chat.models import Chat, Group, Member, Connected_channel, Online
from channels.layers import get_channel_layer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Add channnel to database
        await self.add_channel(user = str(self.scope["user"]), group = self.room_name, channel_name = self.channel_name)

        print("Connected")
        await self.accept()

        # Send previous chat messages on connect
        await self.send(text_data=json.dumps({
            "chat" : await self.get_previous_chats(self.room_name),
        }))

        user_channel_check = await self.check_other_channels(user = str(self.scope["user"]), group = self.room_name)

        user_online_check = await self.check_user_online(user = str(self.scope["user"]), group = self.room_name)

        # Check if user has no channel name stored and is not already in the online database
        if (user_channel_check == True) and (user_online_check == False):
            await self.add_user_online(user = str(self.scope["user"]), group = self.room_name)

        # Send the number of members and users online to all group individuals
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                "members" : await self.group_mebers(self.room_name),
                "online_users" : await self.users_online(self.room_name)
            }
        )

    async def disconnect(self, close_code):
        # Delete the channel name from the database when user disconnects 
        await self.delete_channel(user = str(self.scope["user"]), group = self.room_name, channel_name = self.channel_name)

        # Check if user still has a channel name on the database in order to open the connection
        user_channel_check = await self.check_other_channels(user = str(self.scope["user"]), group = self.room_name)

        # If user doesn't have any other channel name in the database, then websocket should notify others group members
        if user_channel_check != True:
            await self.delete_user_online(user = str(self.scope["user"]), group = self.room_name)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    "members" : await self.group_mebers(self.room_name),
                    "online_users" : await self.users_online(self.room_name),
                }
            )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        date = str(datetime.now())
        date_to_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_to_12h = datetime.strptime(date_to_string, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %I:%M:%S %p")
        message = text_data_json['message']
        user = str(self.scope["user"])
        group = self.room_name
        chat = [
                {
                    "user" : user,
                    "message" : message,
                    "date" : date_to_12h,
                },
            ]

        # Save each message sent between users to the database
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
        if (len(tuple(event.keys())) == 2) and ("chat" in tuple(event.keys())):
            chat = event["chat"]

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                "chat" : chat,
            }))

        else:
             # Send message to WebSocket
            await self.send(text_data=json.dumps({
                "members" : event["members"],
                "online_users" : event["online_users"]
            }))
  

    # Get the previous chats
    @database_sync_to_async
    def get_previous_chats(self, group):
        group_id = Group.objects.filter(name = group)[0]
        chat_query = Chat.objects.filter(group_id = group_id)
        chats = list(chat_query.values())

        for chat in chats:
            date_to_string = chat["date"].strftime("%Y-%m-%d %H:%M:%S")
            date_to_12h = datetime.strptime(date_to_string, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %I:%M:%S %p")
            chat["date"] = date_to_12h
            chat["user_id"] = str(User.objects.filter(id = chat["user_id"])[0])
        return json.dumps(chats)

    # Save the current chat message
    @database_sync_to_async
    def save_chat(self, user, group, message, date):
        user_id = User.objects.filter(username = user)[0].id
        group_id = Group.objects.filter(name = group)[0].id
        chat_save = Chat(user_id = user_id, group_id = group_id, date = date, message = message)
        chat_save.save()

    # Add the current channel name to the database
    @database_sync_to_async
    def add_channel(self, group, user, channel_name):
        user_id = User.objects.filter(username = user)[0].id
        group_id = Group.objects.filter(name = group)[0].id
        save_channel = Connected_channel(user_id = user_id, group_id = group_id, channel_name = channel_name)
        save_channel.save()

    # Delete the channel name
    @database_sync_to_async
    def delete_channel(self, group, user, channel_name):
        user_id = User.objects.filter(username = user)[0].id
        group_id = Group.objects.filter(name = group)[0].id
        delete_channel = Connected_channel.objects.filter(user_id = user_id, group_id = group_id, channel_name = channel_name)
        delete_channel.delete()
    
    # Check if user still has other channel names
    @database_sync_to_async
    def check_other_channels(self, group, user):
        user_id = User.objects.filter(username = user)[0].id
        group_id = Group.objects.filter(name = group)[0].id
        user_channel_exists = Connected_channel.objects.filter(user_id = user_id, group_id = group_id).exists()
        return user_channel_exists

    #Get the group members
    @database_sync_to_async
    def group_mebers(self, group):
        group_id = Group.objects.filter(name = group)[0].id
        group_members = Member.objects.filter(group_id = group_id)
        group_members_list = list(group_members.values())
        for member in group_members_list:
            member["user_id"] = str(User.objects.filter(id = member["user_id"])[0])
        return json.dumps(group_members_list)
    
    # Add user to online database
    @database_sync_to_async
    def add_user_online(self, group, user):
        user_id = User.objects.filter(username = user)[0].id
        group_id = Group.objects.filter(name = group)[0].id
        add_online = Online(user_id = user_id, group_id = group_id)
        add_online.save()

    # Check if a user is online
    @database_sync_to_async
    def check_user_online(self, group, user):
        user_id = User.objects.filter(username = user)[0].id
        group_id = Group.objects.filter(name = group)[0].id
        check_online = Online.objects.filter(user_id = user_id, group_id = group_id).exists()
        return check_online

    # Delete user fron the online database
    @database_sync_to_async
    def delete_user_online(self, group, user):
        user_id = User.objects.filter(username = user)[0].id
        group_id = Group.objects.filter(name = group)[0].id
        delete_user_online = Online.objects.filter(user_id = user_id, group_id = group_id)
        delete_user_online.delete()

    # Get all users in the online database
    @database_sync_to_async
    def users_online(self, group):
        group_id = Group.objects.filter(name = group)[0].id
        users = Online.objects.filter(group_id = group_id)
        users_list = list(users.values())
        for user in users_list:
            user["user_id"] = str(User.objects.filter(id = user["user_id"])[0])
        
        return json.dumps(users_list)

