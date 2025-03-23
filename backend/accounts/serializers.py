from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'avatar', 'bio', 'created_at']

    def to_representation(self, instance):
        # 获取默认表示
        ret = super().to_representation(instance)
        # 如果头像为空，设置默认头像URL
        if not ret['avatar']:
            ret['avatar'] = None  # 前端会处理默认头像
        return ret


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate(self, attrs):
        # 检查用户名是否已存在
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError(
                {"username": "Username already exists."})

        # 检查邮箱是否已存在
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "Email already in use."})

        try:
            # 密码验证
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e)})

        return attrs

    def create(self, validated_data):
        # 创建用户
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )

        # 设置密码 - 使用set_password确保密码被正确哈希
        user.set_password(validated_data['password'])
        user.save()

        # 创建用户个人资料
        Profile.objects.create(user=user)

        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
