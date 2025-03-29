import os
import uuid
import base64
import cloudinary
import cloudinary.uploader
import cloudinary.api
from datetime import datetime
import io


def upload_dalle_image(base64_image, folder="dalle_images"):
    """
    将DALL-E生成的base64编码图片上传到Cloudinary

    参数:
        base64_image: DALL-E返回的base64编码图片字符串
        folder: Cloudinary上存储的文件夹名称

    返回:
        dict: 包含上传结果的字典，成功时包含URL等信息
    """
    try:
        # 处理base64字符串 (处理可能的data:image/png;base64,前缀)
        if ',' in base64_image:
            # 从完整的base64字符串(如data:image/png;base64,xxxxx)中提取实际内容
            image_data = base64_image.split(',')[1]
        else:
            # 已经是纯base64内容
            image_data = base64_image

        # 解码base64为二进制数据
        decoded_image = base64.b64decode(image_data)

        # 生成唯一的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        filename = f"dalle_{timestamp}_{unique_id}"

        # 上传到Cloudinary
        upload_result = cloudinary.uploader.upload(
            io.BytesIO(decoded_image),
            public_id=filename,
            folder=folder,
            resource_type="image",
            # 可选的图片处理设置
            transformation=[
                {'quality': 'auto'},  # 自动优化质量
                {'fetch_format': 'auto'}  # 自动选择最佳格式
            ]
        )

        return {
            'success': True,
            'url': upload_result['secure_url'],  # HTTPS URL
            'public_id': upload_result['public_id'],
            'format': upload_result.get('format'),
            'width': upload_result.get('width'),
            'height': upload_result.get('height'),
            'bytes': upload_result.get('bytes')
        }
    except Exception as e:
        print(f"Cloudinary上传错误: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def delete_cloudinary_image(public_id):
    """
    从Cloudinary删除图片

    参数:
        public_id: 要删除的图片的public_id

    返回:
        dict: 包含删除操作结果的字典
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return {
            'success': result['result'] == 'ok',
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
