import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import base64
import requests
from aigm.utils import upload_dalle_image

# 加载环境变量
load_dotenv()

# 手动配置Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


def test_configuration():
    """测试Cloudinary配置是否正确"""
    config = cloudinary.config()
    print("Cloudinary配置:")
    print(f"Cloud Name: {config.cloud_name}")
    print(f"API Key: {config.api_key[:5]}...")
    print(f"API Secret: {config.api_secret[:5]}...")

    return all([config.cloud_name, config.api_key, config.api_secret])


def test_url_upload():
    """测试通过URL上传图片"""
    print("\n测试从URL上传图片...")

    # 使用一个示例图片URL (选择一个公开可访问的稳定图片URL)
    test_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"

    try:
        # 从URL下载图片
        response = requests.get(test_url)
        if response.status_code != 200:
            print(f"无法下载测试图片: {response.status_code}")
            return False

        # 转换为base64
        image_base64 = base64.b64encode(response.content).decode('utf-8')

        # 上传到Cloudinary
        result = upload_dalle_image(
            image_base64, folder="test_upload_from_url")

        if result['success']:
            print("✅ 上传成功!")
            print(f"图片URL: {result['url']}")
            print(f"Public ID: {result['public_id']}")

            # 可选：删除测试图片
            delete_result = cloudinary.uploader.destroy(result['public_id'])
            print(
                f"清理测试图片: {'成功' if delete_result['result'] == 'ok' else '失败'}")

            return True
        else:
            print(f"❌ 上传失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("=== Cloudinary集成测试 (修改后) ===\n")

    # 测试配置
    config_ok = test_configuration()
    print(f"\n配置检查: {'✅ 正确' if config_ok else '❌ 出错'}")

    if config_ok:
        # 测试URL上传
        upload_ok = test_url_upload()
        print(f"\n上传测试: {'✅ 成功' if upload_ok else '❌ 失败'}")

        if upload_ok:
            print("\n🎉 测试成功! 修改后的代码可以正确工作。")
        else:
            print("\n⚠️ 上传测试失败，需要进一步检查。")
    else:
        print("\n⚠️ Cloudinary配置测试失败。")
