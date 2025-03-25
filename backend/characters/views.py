from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Character
from .serializers import CharacterSerializer, CharacterListSerializer
import logging

logger = logging.getLogger(__name__)


class CharacterViewSet(viewsets.ModelViewSet):
    """角色视图集，提供CRUD操作"""
    serializer_class = CharacterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """只返回当前用户的角色"""
        return Character.objects.filter(user=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        """根据操作类型选择不同的序列化器"""
        if self.action == 'list':
            return CharacterListSerializer
        return CharacterSerializer

    def create(self, request, *args, **kwargs):
        """创建角色"""
        logger.info(f"用户创建角色: {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        """执行创建角色"""
        serializer.save()

    @action(detail=False, methods=['get'])
    def count(self, request):
        """获取当前用户的角色数量"""
        count = self.get_queryset().count()
        return Response({'count': count})
