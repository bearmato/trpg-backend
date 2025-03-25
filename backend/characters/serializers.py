from rest_framework import serializers
from .models import Character


class CharacterSerializer(serializers.ModelSerializer):
    """角色序列化器,用于API的数据转换"""
    portrait_url = serializers.URLField(required=False)

    class Meta:
        model = Character
        fields = ['id', 'name', 'race', 'subrace', 'character_class', 'subclass',
                  'level', 'background', 'background_story', 'personality', 'ideal',
                  'bond', 'flaw', 'alignment', 'gender', 'features', 'portrait_url',
                  'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom',
                  'charisma', 'skill_proficiencies', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        # 确保 user 字段被正确设置
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CharacterListSerializer(serializers.ModelSerializer):
    """角色列表序列化器，返回简化的角色信息用于列表展示"""
    portrait_url = serializers.URLField(required=False)

    class Meta:
        model = Character
        fields = ['id', 'name', 'race', 'character_class', 'level', 'background',
                  'portrait_url', 'created_at', 'updated_at']
