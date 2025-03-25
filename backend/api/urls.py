from django.urls import path, include

urlpatterns = [
    path("aigm/", include("aigm.urls")),  # AIGM 相关 API
    path("rules/", include("rules.urls")),  # 规则查询 API
    path("auth/", include("accounts.urls")),  # 用户认证API
    path("characters/", include("characters.urls")),  # 角色管理API
]
