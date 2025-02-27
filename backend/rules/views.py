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

            # 对特定类型的数据进行额外处理
            processed_data = process_rule_data(data, category)

            # 存入缓存
            cache.set(cache_key, processed_data, CACHE_TIMEOUT)
            return JsonResponse(processed_data)

        return JsonResponse({"error": "Rule not found", "status_code": response.status_code}, status=404)

    except requests.RequestException as e:
        return JsonResponse({"error": f"API request failed: {str(e)}"}, status=500)


def process_rule_data(data, category):
    """
    处理不同类型的规则数据，确保返回更有意义的信息
    """
    # 如果数据已经有描述，直接返回
    if data.get('desc'):
        return data

    # 对于没有描述的数据，尝试构建描述
    processed_data = data.copy()

    # 根据不同类型的数据，生成描述信息
    if category == 'equipment':
        # 为装备添加描述信息
        details = []

        # 添加成本信息
        if data.get('cost'):
            details.append(
                f"Cost: {data['cost'].get('quantity', 0)} {data['cost'].get('unit', '')}")

        # 添加装备类型
        if data.get('equipment_category'):
            details.append(
                f"Category: {data['equipment_category'].get('name', 'Unknown')}")

        # 添加重量信息
        if data.get('weight'):
            details.append(f"Weight: {data['weight']} lbs")

        # 如果有额外的描述性属性
        for key in ['special', 'properties']:
            if data.get(key):
                details.append(
                    f"{key.capitalize()}: {', '.join(prop.get('name', '') for prop in data[key])}")

        # 如果有详细信息，则合并
        if details:
            processed_data['desc'] = "\n".join(details)
        else:
            processed_data['desc'] = "No specific details available for this item."

    # 为其他类型添加类似的处理逻辑
    # elif category == 'spells':
    #     # 处理法术的特殊逻辑

    return processed_data
