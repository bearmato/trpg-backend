from aigm.utils import upload_dalle_image
import cloudinary.uploader
import cloudinary
import os
import base64
import django
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# 导入所需模块

# 手动配置Cloudinary (确保在测试中能正确初始化)
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


def test_cloudinary_config():
    """测试Cloudinary配置是否正确"""
    print("当前Cloudinary配置:")
    print(f"Cloud Name: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
    print(f"API Key: {os.getenv('CLOUDINARY_API_KEY')[:5]}...")  # 隐藏部分API密钥

    # 验证Cloudinary配置是否已应用
    config = cloudinary.config()
    print("\nCloudinary SDK配置:")
    print(f"Cloud Name: {config.cloud_name}")
    print(f"API Key: {config.api_key[:5]}...")

    return config.cloud_name is not None and config.api_key is not None and config.api_secret is not None


def test_upload_simple_image():
    """测试上传一个简单的测试图片到Cloudinary"""
    print("\n测试上传简单图片...")

    # 创建一个简单的测试图片数据 (1x1像素红色PNG)
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

    try:
        # 使用我们的工具函数上传
        result = upload_dalle_image(test_image_data, folder="test_uploads")

        if result['success']:
            print("✅ 上传成功!")
            print(f"图片URL: {result['url']}")
            print(f"Public ID: {result['public_id']}")

            # 可选：删除测试图片
            delete_result = cloudinary.uploader.destroy(result['public_id'])
            print(
                f"\n清理测试图片: {'成功' if delete_result['result'] == 'ok' else '失败'}")

            return True
        else:
            print(f"❌ 上传失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        return False


if __name__ == "__main__":
    print("=== Cloudinary 集成测试 ===\n")

    # 测试配置
    config_ok = test_cloudinary_config()
    print(f"\n配置检查: {'✅ 正确' if config_ok else '❌ 出错'}")

    if config_ok:
        # 测试上传
        upload_ok = test_upload_simple_image()
        print(f"\n上传测试: {'✅ 成功' if upload_ok else '❌ 失败'}")

        # 总结
        if upload_ok:
            print("\n🎉 Cloudinary集成测试完全成功! 您的系统已正确配置和可以使用。")
        else:
            print("\n⚠️ 配置正确但上传测试失败，请检查网络连接和API权限。")
    else:
        print("\n⚠️ Cloudinary配置测试失败，请检查环境变量和settings.py配置。")
