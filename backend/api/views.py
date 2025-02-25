import os
from openai import OpenAI
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response

# 加载 .env 配置
load_dotenv()

# 获取 API Key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@api_view(["POST"])
def ai_gm_chat(request):
    """
    处理 AI GM 聊天的 API 端点
    """
    user_input = request.data.get("message", "")

    if not user_input:
        return Response({"error": "Message cannot be empty"}, status=400)

    try:
        # 发送消息到 OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",  # 最新模型
            messages=[
                {"role": "system", "content": "You are a Game Master in a tabletop RPG."},
                {"role": "user", "content": user_input},
            ],
            temperature=1,
            max_tokens=300,  # 限制回复长度
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # 获取 AI 响应
        ai_reply = response.choices[0].message.content

        return Response({"reply": ai_reply}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
