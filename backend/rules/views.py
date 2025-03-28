# backend/rules/views.py
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
        'title': 'D&D 5e PlayersHandbook',
        'description': 'Essential reference for every Dungeons & Dragons roleplayer. Includes rules for character creation, exploration, and adventure.',
        'category': 'core'
    },
    'DungeonMastersGuide.pdf': {
        'title': 'DungeonMasters Guide',
        'description': ' All the rules and guidance a Dungeon Master needs to craft engaging stories.',
        'category': 'core'
    },
    'MonsterManual.pdf': {
        'title': 'Monster Manual',
        'description': 'Comprehensive compendium of monsters in the game.',
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
    """提供PDF文件预览服务"""
    file_path = PDF_DIR / filename

    # 检查文件是否存在
    if not file_path.exists():
        return JsonResponse({'error': 'PDF文件未找到'}, status=404)

    # 提供文件用于内嵌预览
    response = FileResponse(open(file_path, 'rb'),
                            content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    # 添加跨域头
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    return response


@api_view(['GET'])
def download_pdf(request, filename):
    """提供PDF文件下载服务"""
    file_path = PDF_DIR / filename

    # 检查文件是否存在
    if not file_path.exists():
        return JsonResponse({'error': 'PDF文件未找到'}, status=404)

    # 提供文件 - 使用 attachment 下载
    response = FileResponse(open(file_path, 'rb'),
                            content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # 添加跨域头
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    return response
