from django.http import JsonResponse
import requests

DND_API_BASE_URL = "https://www.dnd5eapi.co/api"


def get_rules(request, category):
    """获取规则类别数据"""
    response = requests.get(f"{DND_API_BASE_URL}/{category}")
    if response.status_code == 200:
        return JsonResponse(response.json())
    return JsonResponse({"error": "Failed to fetch data"}, status=500)


def get_rule_detail(request, category, rule_name):
    """获取规则详情"""
    response = requests.get(f"{DND_API_BASE_URL}/{category}/{rule_name}")
    if response.status_code == 200:
        return JsonResponse(response.json())
    return JsonResponse({"error": "Rule not found"}, status=404)
