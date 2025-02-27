# backend/rules/views.py
from django.http import JsonResponse
import requests
import json
from django.core.cache import cache

DND_API_BASE_URL = "https://www.dnd5eapi.co/api"
CACHE_TIMEOUT = 60 * 60 * 24  # 24小时缓存


def get_rules(request, category):
    """从 D&D 5e API 获取规则数据"""
    # 尝试从缓存获取
    cache_key = f"dnd_rules_{category}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return JsonResponse(cached_data)

    try:
        response = requests.get(f"{DND_API_BASE_URL}/{category}")
        if response.status_code == 200:
            data = response.json()
            # 存入缓存
            cache.set(cache_key, data, CACHE_TIMEOUT)
            return JsonResponse(data)
        return JsonResponse({"error": "Failed to fetch data", "status_code": response.status_code}, status=500)
    except requests.RequestException as e:
        return JsonResponse({"error": f"API request failed: {str(e)}"}, status=500)


def get_rule_detail(request, category, rule_name):
    """获取单个规则详情"""
    # 尝试从缓存获取
    cache_key = f"dnd_rule_detail_{category}_{rule_name}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return JsonResponse(cached_data)

    try:
        response = requests.get(f"{DND_API_BASE_URL}/{category}/{rule_name}")
        if response.status_code == 200:
            data = response.json()
            # 存入缓存
            cache.set(cache_key, data, CACHE_TIMEOUT)
            return JsonResponse(data)
        return JsonResponse({"error": "Rule not found", "status_code": response.status_code}, status=404)
    except requests.RequestException as e:
        return JsonResponse({"error": f"API request failed: {str(e)}"}, status=500)
