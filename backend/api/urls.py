from django.urls import path
from .views import ai_gm_chat

urlpatterns = [
    path("chat/", ai_gm_chat, name="ai_gm_chat"),
]
