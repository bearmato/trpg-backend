from django.apps import AppConfig


class RulesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # 自动生成数据库表，用64位的数字来编号
    name = "rules"  # 应用名称
