from django.urls import path
from .views import ai_gm_chat, generate_character_background, generate_character_portrait, delete_image

urlpatterns = [
    path("chat/", ai_gm_chat),  # 访问 /api/aigm/chat/
    # Access via /api/aigm/character-background
    path("character-background/", generate_character_background),
    # Access via /api/aigm/character-portrait
    path("character-portrait/", generate_character_portrait),
    # 删除Cloudinary上的图片
    path("delete-image/<str:public_id>/", delete_image),
]
