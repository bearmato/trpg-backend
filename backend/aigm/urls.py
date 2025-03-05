from django.urls import path
from .views import ai_gm_chat, ai_gm_adventure_start, generate_character_background

urlpatterns = [
    path("chat/", ai_gm_chat),  # 访问 /api/aigm/chat/
    # Access via /api/aigm/adventure-start/
    path("adventure-start/", ai_gm_adventure_start),
    # Access via /api/aigm/character-backgrou
    path("character-background/", generate_character_background),
]
