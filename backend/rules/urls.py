from django.urls import path
from .views import get_rules, get_rule_detail

urlpatterns = [
    path("rules/<str:category>/", get_rules),
    path("rules/<str:category>/<str:rule_name>/", get_rule_detail),
]
