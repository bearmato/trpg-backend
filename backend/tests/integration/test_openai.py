import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# 添加项目根目录到路径，以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

# 加载环境变量
load_dotenv()

# 初始化OpenAI客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def test_openai_connection():
    """测试与OpenAI API的连接是否正常工作"""
    print("=== OpenAI API 连接测试 ===\n")

    try:
        # 发送简单的测试请求
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            max_tokens=50
        )

        # 获取回复
        reply = response.choices[0].message.content

        print(f"✅ API 响应成功!")
        print(f"回复内容: {reply[:50]}...")

        return True
    except Exception as e:
        print(f"❌ API 请求失败: {str(e)}")
        return False


def test_dalle_api():
    """测试DALL-E API是否正常工作"""
    print("\n=== DALL-E API 测试 ===\n")

    try:
        # 发送简单的图像生成请求
        response = client.images.generate(
            model="dall-e-3",
            prompt="A simple blue circle on a white background",
            size="1024x1024",
            quality="standard",
            n=1,
        )

        # 获取图像URL
        image_url = response.data[0].url

        print(f"✅ DALL-E API 响应成功!")
        print(f"图像URL: {image_url[:60]}...")

        return True
    except Exception as e:
        print(f"❌ DALL-E API 请求失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 测试OpenAI连接
    openai_ok = test_openai_connection()
    print(f"\nOpenAI连接测试: {'✅ 成功' if openai_ok else '❌ 失败'}")

    # 测试DALL-E API
    if openai_ok:
        dalle_ok = test_dalle_api()
        print(f"\nDALL-E API测试: {'✅ 成功' if dalle_ok else '❌ 失败'}")

        # 总结
        if dalle_ok:
            print("\n🎉 所有OpenAI API测试成功!")
        else:
            print("\n⚠️ DALL-E API测试失败，但基本连接正常。")
    else:
        print("\n⚠️ 无法连接到OpenAI API，请检查API密钥和网络连接。")
