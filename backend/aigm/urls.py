from django.urls import path
from .views import ai_gm_chat

urlpatterns = [
    path("chat/", ai_gm_chat),  # 访问 /api/aigm/chat/
]
