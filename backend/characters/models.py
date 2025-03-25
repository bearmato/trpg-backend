from django.db import models
from django.contrib.auth.models import User


class Character(models.Model):
    """角色模型，用于存储用户创建的角色信息"""
    # 基本信息
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=100)
    race = models.CharField(max_length=50)
    subrace = models.CharField(max_length=50, blank=True, null=True)
    character_class = models.CharField(max_length=50)
    subclass = models.CharField(max_length=50, blank=True, null=True)
    level = models.IntegerField(default=1)
    background = models.CharField(max_length=50)
    alignment = models.CharField(max_length=50)
    gender = models.CharField(max_length=20, default='male')

    # 属性
    strength = models.IntegerField(default=10)
    dexterity = models.IntegerField(default=10)
    constitution = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)
    wisdom = models.IntegerField(default=10)
    charisma = models.IntegerField(default=10)

    # 技能、外观和故事
    skill_proficiencies = models.JSONField(default=list)  # 存储技能列表
    features = models.JSONField(default=list)  # 存储外观特征
    background_story = models.TextField(blank=True, null=True)
    personality = models.TextField(blank=True, null=True)
    ideal = models.TextField(blank=True, null=True)
    bond = models.TextField(blank=True, null=True)
    flaw = models.TextField(blank=True, null=True)

    # 图像
    portrait_url = models.URLField(max_length=500, blank=True, null=True)

    # 元数据
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.race} {self.character_class} (Level {self.level})"
