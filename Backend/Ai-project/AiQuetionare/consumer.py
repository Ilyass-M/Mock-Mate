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
