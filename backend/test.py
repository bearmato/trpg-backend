import openai
import os

# 读取 API Key（如果你在 .env 里配置了）
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-xxxxx")

# 发送测试请求
try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello, how are you?"}]
    )
    print("✅ API 响应成功: ", response["choices"][0]["message"]["content"])
except openai.error.OpenAIError as e:
    print("❌ API 请求失败: ", e)
