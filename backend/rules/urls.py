from django.urls import path
from .views import get_rulebooks, view_pdf

urlpatterns = [
    path("books/", get_rulebooks),  # 获取所有规则书
    path("pdf/<str:filename>/", view_pdf),  # 查看指定PDF
]
