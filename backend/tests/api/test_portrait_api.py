import requests
import json
import time


def test_character_portrait_api():
    """测试角色肖像生成API，验证Cloudinary上传功能"""

    print("=== 角色肖像生成API测试 ===\n")

    # API端点
    api_url = "http://localhost:8000/api/aigm/character-portrait/"

    # 测试数据
    test_data = {
        "name": "测试角色",
        "race": "人类 (Human)",
        "class": "战士 (Fighter)",
        "gender": "male",
        "style": "watercolor",  # 使用水彩风格便于快速识别
        "features": ["短发", "微笑", "友善的眼神"]
    }

    print(f"发送请求到 {api_url}...")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")

    try:
        # 发送请求
        start_time = time.time()
        response = requests.post(api_url, json=test_data)
        elapsed_time = time.time() - start_time

        # 处理响应
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ API调用成功! (耗时: {elapsed_time:.2f}秒)")
            print(f"图片URL: {data.get('image_url')}")
            print(f"Public ID: {data.get('public_id')}")

            # 验证是否是Cloudinary URL
            if "cloudinary.com" in data.get('image_url', ''):
                print("\n✅ 确认是Cloudinary URL")
                print("\n🎉 测试完全成功! 角色图像已生成并成功上传到Cloudinary。")
                return True
            else:
                print("\n❌ URL不是Cloudinary地址，可能没有正确保存")
                return False
        else:
            print(f"\n❌ API调用失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {str(e)}")
        return False


if __name__ == "__main__":
    test_character_portrait_api()
