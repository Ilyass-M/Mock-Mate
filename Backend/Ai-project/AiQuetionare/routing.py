
from django.urls import path
# from .consumers import *
from AiQuetionare.consumer import * 
websocket_urlpatterns = [
    path('interview/<str:job_desc_id>/', InterviewConsumer.as_asgi()),
    # path('chat/group/<str:group_id>/', ChatConsumer.as_asgi()),
    # path('ws/notification/', NotificationConsumer.as_asgi()),
    # path('ws/typing/', TypingConsumer.as_asgi()),
    # path('ws/online-status/', OnlineStatusConsumer.as_asgi()),
]
