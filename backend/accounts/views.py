from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer, ProfileUpdateSerializer
from .models import Profile
import cloudinary
import cloudinary.uploader
import uuid
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated


import logging
logger = logging.getLogger(__name__)


class RegisterView(APIView):
    def post(self, request):
        logger.info(f"收到注册请求: {request.data}")

        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                logger.info(f"用户注册成功: {user.username}")
                return Response({
                    'user': UserSerializer(user).data,
                    'token': token.key
                }, status=status.HTTP_201_CREATED)

            logger.warning(f"注册验证失败: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"注册异常: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Delete the token to logout
            request.user.auth_token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileUpdateSerializer(
            profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(ProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """Handle avatar upload to Cloudinary"""
        try:
            # Get the uploaded file
            avatar_file = request.FILES.get('avatar')
            if not avatar_file:
                return Response(
                    {'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file size (3MB max)
            if avatar_file.size > 3 * 1024 * 1024:
                return Response(
                    {'error': 'Image size should not exceed 3MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate a unique filename
            filename = f"avatar_{uuid.uuid4().hex}"

            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                avatar_file,
                public_id=filename,
                folder="user_avatars",
                resource_type="image",
                transformation=[
                    {'quality': 'auto'},
                    {'fetch_format': 'auto'},
                    {'width': 400, 'height': 400, 'crop': 'limit'}
                ]
            )

            # Get the secure URL from Cloudinary
            avatar_url = upload_result.get('secure_url')

            # Update user's profile
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.avatar = avatar_url
            profile.save()

            # Return the updated profile
            serializer = ProfileSerializer(profile)
            return Response({
                'message': 'Avatar uploaded successfully',
                'avatar_url': avatar_url,
                'profile': serializer.data
            })

        except Exception as e:
            return Response(
                {'error': f'Failed to upload avatar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
