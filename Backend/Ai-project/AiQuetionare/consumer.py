import json
import urllib.parse
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from AiQuetionare.models import *
from AiQuetionare.serializer import *
from asgiref.sync import sync_to_async
from asgiref.sync import SyncToAsync 
from asgiref.sync import sync_to_async


class InterviewConsumer(AsyncWebsocketConsumer):
    async def get_job_description(self, job_desc_id):
        try:
            job_description = await sync_to_async(JobDescription.objects.get)(id=job_desc_id)
            return job_description
        except JobDescription.DoesNotExist:
            return None
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['job_desc_id']
            if self.scope['user'].is_anonymous:
            # print("Unauthenticated user attempted to connect.")
                await self.close(code=401)
                return

            get_job_description = await self.get_job_description(self.room_name)
            if not get_job_description:
                # print("Job description not found.")
                await self.close(code=404)
                return
            user_id = self.scope['user'].id
            self.room_group_name = f'interview_{self.room_name}_userid{user_id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        except Exception as e:
            print(f"Error in connect: {e}")
            await self.close()
    async def disconnect(self, close_code):
        try:
            # Leave the group
            self.room_name = self.scope['url_route']['kwargs']['job_desc_id']
            user_id = self.scope['user'].id
            self.room_group_name = f'chat_jd_{self.room_name}_userid{user_id}'
            
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Error in disconnect: {e}")

    