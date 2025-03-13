from django.urls import path
from .views import ai_gm_chat, generate_character_background, generate_character_portrait

urlpatterns = [
    path("chat/", ai_gm_chat),  # 访问 /api/aigm/chat/
    # Access via /api/aigm/character-background
    path("character-background/", generate_character_background),
    # Access via /api/aigm/character-portrait
    path("character-portrait/", generate_character_portrait),
]
