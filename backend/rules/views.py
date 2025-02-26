from django.http import JsonResponse
import requests

DND_API_BASE_URL = "https://www.dnd5eapi.co/api"


def get_rules(request, category):
    """从 D&D 5e API 获取规则数据"""
    response = requests.get(f"{DND_API_BASE_URL}/{category}")
    if response.status_code == 200:
        return JsonResponse(response.json())
    return JsonResponse({"error": "Failed to fetch data"}, status=500)


def get_rule_detail(request, category, rule_name):
    """获取单个规则详情"""
    response = requests.get(f"{DND_API_BASE_URL}/{category}/{rule_name}")
    if response.status_code == 200:
        return JsonResponse(response.json())
    return JsonResponse({"error": "Rule not found"}, status=404)
