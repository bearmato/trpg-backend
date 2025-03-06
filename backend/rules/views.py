from django.http import FileResponse, JsonResponse
from django.conf import settings
import os
from rest_framework.decorators import api_view
from pathlib import Path

# PDF 文件目录路径 - 您需要在此位置存储PDF文件
PDF_DIR = Path(settings.BASE_DIR) / 'pdfs'

# 预定义的PDF元数据
PDF_METADATA = {
    'DnD5ePlayersHandbook.pdf': {
        'title': 'D&D 5e 玩家手册',
        'description': '每位龙与地下城角色扮演者必备的基础参考。包含角色创建、探索和冒险的规则。',
        'category': 'core'
    },
    'DungeonMastersGuide.pdf': {
        'title': '地下城主指南',
        'description': '地下城主打造传奇故事所需的一切指南，世界最伟大的角色扮演游戏。',
        'category': 'core'
    },
    'MonsterManual.pdf': {
        'title': '怪物图鉴',
        'description': '世界最伟大的角色扮演游戏中致命怪物的详尽图鉴。',
        'category': 'core'
    }
}


@api_view(['GET'])
def get_rulebooks(request):
    """返回所有可用的规则书分类及PDF文件"""
    # 确保目录存在
    if not PDF_DIR.exists():
        os.makedirs(PDF_DIR, exist_ok=True)

    # 扫描目录并构建分类列表
    rulebooks = {}
    for file in PDF_DIR.glob('*.pdf'):
        filename = file.name

        # 获取元数据或使用默认值
        metadata = PDF_METADATA.get(filename, {
            'title': filename,
            'description': '规则书PDF文件',
            'category': 'other'
        })

        # 添加文件信息
        file_info = {
            'filename': filename,
            'title': metadata['title'],
            'description': metadata['description'],
            'size': file.stat().st_size,
            'url': f'/api/rules/pdf/{filename}'
        }

        # 按分类组织
        category = metadata.get('category', 'other')
        if category not in rulebooks:
            rulebooks[category] = []

        rulebooks[category].append(file_info)

    # 分类名称映射
    category_names = {
        'core': '核心规则书',
        'adventure': '冒险模组',
        'supplement': '补充规则',
        'other': '其他规则资源'
    }

    # 构建最终响应
    result = []
    for category, books in rulebooks.items():
        result.append({
            'id': category,
            'name': category_names.get(category, category),
            'books': books
        })

    return JsonResponse({
        'status': 'success',
        'data': result
    })


@api_view(['GET'])
def view_pdf(request, filename):
    """提供PDF文件服务"""
    file_path = PDF_DIR / filename

    # 检查文件是否存在
    if not file_path.exists():
        return JsonResponse({'error': 'PDF文件未找到'}, status=404)

    # 提供文件
    response = FileResponse(open(file_path, 'rb'),
                            content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
