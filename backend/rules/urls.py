from django.urls import path
from .views import get_rules, get_rule_detail

urlpatterns = [
    path("<str:category>/", get_rules),  # 访问 /api/rules/spells/
    # 访问 /api/rules/spells/fireball/
    path("<str:category>/<str:rule_name>/", get_rule_detail),
]
