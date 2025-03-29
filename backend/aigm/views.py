import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import upload_dalle_image, delete_cloudinary_image

# Load .env configuration
load_dotenv()

# Get API Key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt - Detailed Game Master role definition
SYSTEM_PROMPT = """You are an experienced Game Master (GM) for tabletop role-playing games (TRPG).
Your task is to create engaging fantasy worlds, tell vivid stories, manage game rules, and play all NPCs except the player characters.

As a GM, you should:
1. Create detailed and immersive scene descriptions
2. Play various NPCs, giving them unique voices and personalities
3. Explain and apply game rules fairly
4. Advance the story based on player actions
5. Provide suggestions when needed, while respecting player decisions
6. Maintain story flow and coherence
7. Create memorable adventure experiences

Respond to any player request in your role as GM. Use vivid language to create an immersive experience.

IMPORTANT: If a player asks about rolling dice or making checks, remind them to use the floating dice button in the bottom right corner of the page. DO NOT try to roll dice for them or describe results - just remind them about the dice button.

Follow the classic TRPG format, including scene setting, NPC dialogue, and combat sequence execution.
"""


@api_view(["POST"])
def ai_gm_chat(request):
    """API endpoint for interacting with AI GM"""

    # Get user input and conversation history
    user_input = request.data.get("message", "")
    conversation_history = request.data.get("history", [])

    if not user_input:
        return Response({"error": "Message cannot be empty"}, status=400)

    try:
        # Build message history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history (if any)
        for msg in conversation_history:
            role = "assistant" if msg["role"] == "gm" else "user"
            messages.append({"role": role, "content": msg["text"]})

        # Add current user input
        messages.append({"role": "user", "content": user_input})

        # Send message to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",  # Use latest model
            messages=messages,
            temperature=0.7,  # Moderate creativity
            max_tokens=800,   # Increased reply length
            top_p=1,
            frequency_penalty=0.2,  # Slightly reduce repetition
            presence_penalty=0.2    # Encourage topic variation
        )

        # Get AI response
        ai_reply = response.choices[0].message.content

        return Response({"reply": ai_reply}, status=200)

    except Exception as e:
        # Log detailed error information
        print(f"AI GM request error: {str(e)}")
        return Response({"error": f"Error communicating with AI: {str(e)}"}, status=500)


@api_view(["POST"])
def generate_character_background(request):
    """根据D&D规则生成角色背景故事，支持中英文选择"""

    # 获取角色信息
    character_name = request.data.get("name", "")
    character_race = request.data.get("race", "")
    character_class = request.data.get("class", "")
    background = request.data.get("background", "")
    alignment = request.data.get("alignment", "")
    keywords = request.data.get("keywords", [])
    tone = request.data.get("tone", "balanced")
    language = request.data.get("language", "chinese")  # 默认使用中文

    if not character_race or not character_class:
        return Response({"error": "角色种族和职业是必需的"}, status=400)

    try:
        # 基于D&D背景构建详细提示词
        background_details = get_background_details(background)
        alignment_details = get_alignment_details(alignment)

        # 构建关键词列表
        keywords_text = ", ".join(keywords) if keywords else "none specified"

        # 根据所选语言构建提示词
        if language == "chinese":
            background_prompt = f"""作为一位资深《龙与地下城》(D&D 5e)世界设定专家，为以下角色创建一个符合官方规则和设定的中文背景故事：
            
            基本信息:
            - 姓名: {character_name}
            - 种族: {character_race}
            - 职业: {character_class}
            - 背景: {background}
            - 阵营: {alignment}
            - 故事基调: {tone}
            - 关键元素: {keywords_text}
            
            背景详情:
            {background_details}
            
            阵营说明:
            {alignment_details}
            
            请创作一个内容丰富、合理且符合D&D世界观的角色背景故事。故事应当：
            1. 清晰解释该角色如何获得其职业能力
            2. 符合所选背景的特质和特征
            3. 体现所选阵营的价值观和行为模式
            4. 包含角色的成长历程和动机
            5. 自然融入指定的关键词元素
            6. 符合指定的故事基调
            7. 长度适中(约3-5段)，富有叙事性和情感深度
            
            确保生成的背景能够为玩家提供丰富的角色扮演素材，同时与D&D官方规则书中的设定保持一致。
            必须使用中文回答。
            """
        else:  # 英文
            background_prompt = f"""As an expert in Dungeons & Dragons (D&D 5e) world-building, create an official-style background story in English for the following character:
            
            Basic Information:
            - Name: {character_name}
            - Race: {character_race}
            - Class: {character_class}
            - Background: {background}
            - Alignment: {alignment}
            - Story Tone: {tone}
            - Key Elements: {keywords_text}
            
            Background Details:
            {background_details}
            
            Alignment Details:
            {alignment_details}
            
            Please craft a rich, plausible character background story that fits within the D&D universe. The story should:
            1. Clearly explain how the character acquired their class abilities
            2. Reflect the traits and features of their chosen background
            3. Embody the values and behavioral patterns of their alignment
            4. Include the character's journey and motivations
            5. Naturally incorporate the specified key elements
            6. Match the specified story tone
            7. Be of moderate length (about 3-5 paragraphs) with narrative depth and emotional resonance
            
            Ensure the generated background provides rich role-playing material for the player while maintaining consistency with D&D official rulebooks.
            The response must be in English.
            """

        # 发送请求到OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                    "content": "你是龙与地下城世界的资深大师，精通D&D 5e的所有官方背景和阵营规则，并擅长创作符合设定的角色背景故事。"},
                {"role": "user", "content": background_prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0.3,
            presence_penalty=0.3
        )

        # 获取AI响应
        background_story = response.choices[0].message.content

        return Response({
            "background": background_story,
            "name": character_name,
            "race": character_race,
            "class": character_class,
            "alignment": alignment,
            "background_type": background,
            "language": language
        }, status=200)

    except Exception as e:
        return Response({"error": f"生成角色背景时出错: {str(e)}"}, status=500)


def get_background_details(background):
    """获取D&D官方背景的详细说明（保持原样，不需要修改）"""
    background_details = {
        "侍僧 (Acolyte)": """作为侍僧，你在神殿或修道院中度过了光阴，学习传统、仪式和祷告。你可能是虔诚的牧师，或正在寻找信仰真谛。
特性：避难所 - 你与同信仰的宗教组织有联系，可在其圣地获得食宿。
技能熟练：洞悉、宗教
语言：两种自选语言
起始装备：圣徽、祷告书、5根蜡烛、普通服饰、腰包和15金币""",

        "罪犯 (Criminal)": """你曾是一名罪犯，通过非法手段谋生。你可能是小偷、杀手、走私犯或欺诈师。
特性：犯罪联系人 - 你有可靠的情报来源和地下世界联系人，了解犯罪活动和地下网络。
技能熟练：欺骗、隐匿
工具熟练：一种游戏组、盗贼工具
起始装备：撬锁工具、神秘来历的信件、普通服饰、腰包和15金币""",

        "民间英雄 (Folk Hero)": """你来自普通民众，但因某次英勇行为而成为家乡的英雄。你与平民有着深厚联系。
特性：朴素好客 - 普通人会尽可能地隐藏、保护和收留你，甚至冒险帮助你。
技能熟练：驯兽、生存
工具熟练：一种工匠工具、陆上载具
起始装备：工匠工具、铁锹、铁壶、普通服饰、腰包和10金币""",

        "贵族 (Noble)": """你出生或受邀加入上层阶级，拥有财富和特权，可能有家族纹章或徽章。
特性：特权地位 - 人们倾向于认为你拥有权力和权威，你在高等社会中能获得优待。
技能熟练：历史、说服
工具熟练：一种游戏组
语言：一种自选语言
起始装备：精美服饰、纯银戒指、家族身份证明卷轴、腰包和25金币""",

        "贤者 (Sage)": """你一生致力于学习和研究，专注于收集知识和古老的秘密。
特性：研究员 - 当你不知道某信息时，通常知道可以在哪里找到这些信息。
技能熟练：奥秘、历史
语言：两种自选语言
起始装备：墨水笔、墨水瓶、小刀、研究笔记、普通服饰、腰包和10金币""",

        "士兵 (Soldier)": """你曾是一名职业战士，可能是军队或雇佣兵团的一员，了解战争和战术。
特性：军衔 - 你拥有前军旅生涯的军衔，战友认可你的权威和影响力。
技能熟练：运动、威吓
工具熟练：一种游戏组、陆上载具
起始装备：徽章或军衔标志、战利品、骰子或卡牌、普通服饰、腰包和10金币""",

        "流浪儿 (Urchin)": """你在城市街头长大，学会了通过聪明才智和敏捷活下去，熟知城市的秘密通道和角落。
特性：城市秘密 - 你了解城市的秘密通道和小路，能够在城市环境中比他人更快地穿行。
技能熟练：巧手、隐匿
工具熟练：盗贼工具、伪装工具包
起始装备：小刀、城市地图、宠物鼠、家人信物、普通服饰、腰包和10金币""",

        "艺人 (Entertainer)": """你在众人面前表演，以你的音乐、舞蹈、杂耍、讲故事或其他娱乐形式闻名。
特性：名人粉丝 - 在某些地方会有人认出你，给予你免费食宿和小型表演机会。
技能熟练：体操、表演
工具熟练：伪装工具包、一种乐器
起始装备：乐器、崇拜者的情书、旅行服饰、腰包和15金币""",

        "公会工匠 (Guild Artisan)": """你是制作某种商品的技艺大师，属于工匠公会的成员，享有该公会的支持与保护。
特性：公会会员 - 公会成员会提供食宿、法律援助和其他必要帮助。
技能熟练：洞悉、说服
工具熟练：一种工匠工具
语言：一种自选语言
起始装备：工匠工具、公会介绍信、旅行服饰、腰包和15金币""",

        # 可以继续添加其他官方背景
    }

    return background_details.get(background, "你选择的是自定义背景，请根据你的想象力发挥。")


def get_alignment_details(alignment):
    """获取D&D官方阵营的详细说明"""
    alignment_details = {
        "守序善良 (Lawful Good)": """守序善良的角色相信秩序、规则和善良的行为是社会稳定的基础。他们信守诺言，尊重权威，保护弱者，对抗邪恶，但总是遵循法律和传统。这类角色可能是忠诚的骑士、公正的法官或虔诚的牧师，他们将正义与慈悲结合，通过系统性和有组织的方式来实现更大的善。""",

        "中立善良 (Neutral Good)": """中立善良的角色根本上关心的是做好事和帮助他人，而不太关心规则或混乱。他们会做最能带来最大善良结果的事情，无论是否符合法律或传统。这类角色可能是治疗者、慈善家或改革者，他们愿意在必要时弯曲规则来实现善良目标。""",

        "混乱善良 (Chaotic Good)": """混乱善良的角色遵循自己的道德指南，重视个人自由与善良的行为。他们抵抗压迫，蔑视规则，但总是为了更大的善。这类角色可能是义贼、叛军或独立思想家，他们相信善良应该来自个人良知，而不是外部规则或期望。""",

        "守序中立 (Lawful Neutral)": """守序中立的角色信奉秩序、传统和规则高于一切。他们遵循法律的字面意义而非精神，不偏向善恶任何一方。这类角色可能是不偏不倚的法官、忠诚的士兵或奉行传统的修道士，他们认为只有通过结构和规则才能维持社会稳定。""",

        "绝对中立 (True Neutral)": """绝对中立的角色回避极端，追求自然的平衡，或仅仅关注自己的事务而尽量避免道德困境。他们不会偏向任何阵营，而是基于情况做出最实际的决定。这类角色可能是德鲁伊、隐士或实用主义者，他们视平衡为最高目标，或是谨慎地避免卷入更大的冲突。""",

        "混乱中立 (Chaotic Neutral)": """混乱中立的角色珍视自由、本能和冲动高于一切，既不刻意行善也不刻意作恶。他们遵循个人欲望，蔑视规则和期望，追求最大化自由。这类角色可能是放浪形骸的艺术家、无拘无束的游荡者或不可预测的疯子，他们的行动难以预测，但通常出于个人利益或一时兴起。""",

        "守序邪恶 (Lawful Evil)": """守序邪恶的角色有条不紊、有计划地追求邪恶目标，同时维持一套荣誉或忠诚准则。他们利用规则和系统为自己谋取利益，往往遵守承诺，但同时不惜牺牲他人来实现目标。这类角色可能是暴君、组织化的罪犯或军阀，他们通过操控现有系统获取权力和控制。""",

        "中立邪恶 (Neutral Evil)": """中立邪恶的角色毫无原则地追求自身利益，对他人毫不关心。他们会做任何能获取所需的事，不受忠诚或混乱的约束。这类角色可能是冷血杀手、佣兵或纯粹的机会主义者，他们的唯一准则是自我服务，对伤害他人全然无视。""",

        "混乱邪恶 (Chaotic Evil)": """混乱邪恶的角色由暴力、破坏和残忍的冲动驱使，蔑视规则、传统和他人福祉。他们既不可预测又危险，往往因暴力和毁灭本身而行动。这类角色可能是狂徒、虐待狂或恶魔崇拜者，他们在苦难与混乱中找到快乐，不受任何道德约束。"""
    }

    return alignment_details.get(alignment, "你尚未选择阵营，或选择了自定义阵营。")


@api_view(["POST"])
def generate_character_portrait(request):
    """生成具有准确种族和职业特征的角色立绘图像，并保存到Cloudinary"""
    # 获取角色信息
    character_name = request.data.get("name", "")
    character_race = request.data.get("race", "")
    character_subrace = request.data.get("subrace", "")
    character_class = request.data.get("class", "")
    character_gender = request.data.get("gender", "")
    character_style = request.data.get("style", "fantasy")  # 艺术风格
    features = request.data.get("features", [])  # 特征描述

    if not character_race or not character_class:
        return Response({"error": "角色种族和职业是必需的"}, status=400)

    try:
        # 获取详细的种族和职业特征描述
        race_details = get_race_appearance_details(
            character_race, character_subrace)
        class_details = get_class_appearance_details(character_class)

        # 构建详细的图像生成提示词
        portrait_prompt = f"""Create a detailed portrait of a {character_race} {character_class}, {character_gender}.

        ## Race Features:
        {race_details}
        
        ## Class Features:
        {class_details}
        
        ## Character Details:
        - Name: {character_name if character_name else 'Unnamed character'}
        - Style: {character_style} art style
        - Additional Features: {', '.join(features)}
        
        The portrait must accurately represent this D&D character with correct racial and class features.
        Create a high-quality shoulder-up portrait showing the character's face clearly, 
        with appropriate clothing, equipment, expressions, and background elements that
        match both their race and class specialization.
        
        ## Important Requirements:
        - Character must have all canonical racial features as described
        - Clothing and equipment must clearly represent their class
        - Face should be expressive and convey personality
        - Background should subtly hint at character's profession and environment
        """

        # 调用OpenAI的DALL-E 3图像生成API
        response = client.images.generate(
            model="dall-e-3",
            prompt=portrait_prompt,
            size="1024x1024",
            quality="hd",  # 使用高质量设置
            response_format="url",  # 明确指定返回URL
            n=1,
        )

        # 获取生成的图像URL
        image_url = response.data[0].url

        # 下载图像以便上传到Cloudinary
        import requests
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            return Response({
                "error": f"无法下载DALL-E生成的图像，状态码: {image_response.status_code}"
            }, status=500)

        # 将图像内容转换为base64
        import base64
        image_base64 = base64.b64encode(image_response.content).decode('utf-8')

        # 使用Cloudinary保存图像
        folder_name = "character_portraits"
        upload_result = upload_dalle_image(image_base64, folder=folder_name)

        if not upload_result['success']:
            return Response({
                "error": f"图像上传到Cloudinary失败: {upload_result['error']}"
            }, status=500)

        # 返回Cloudinary图像URL和相关信息
        return Response({
            "image_url": upload_result['url'],
            "public_id": upload_result['public_id'],
            "name": character_name,
            "race": character_race,
            "class": character_class,
            "image_details": {
                "width": upload_result.get('width'),
                "height": upload_result.get('height'),
                "format": upload_result.get('format'),
                "size": upload_result.get('bytes')
            }
        }, status=200)

    except Exception as e:
        import traceback
        print(f"生成角色立绘时出错: {str(e)}")
        print(traceback.format_exc())
        return Response({"error": f"生成角色立绘时出错: {str(e)}"}, status=500)


def get_race_appearance_details(race, subrace=""):
    """获取D&D种族的详细外貌描述，确保图像生成准确反映种族特征"""

    race_appearance = {
        "龙裔 (Dragonborn)": """
            Dragonborn have draconic features including:
            - Scaled body with reptilian appearance
            - Dragon-like head with elongated snout/muzzle
            - Strong draconic eyes
            - Powerful build standing 6'6" tall on average
            - Scale colors vary by draconic ancestry
            - Typically have a tapering tail
            The character is a draconic humanoid with full reptilian features, not a human with dragon accessories.
        """,

        "提夫林 (Tiefling)": """
            Tieflings have fiendish features including:
            - Skin ranging from human tones to red, purple, or blue
            - Curved horns (various shapes possible)
            - Solid-colored eyes (typically red, black, white, silver, gold)
            - Pointed teeth and ears
            - Long thick tail with a pointed tip
            - Some have cloven hooves instead of feet
            - Some have subtle skin patterns resembling sigils
        """,

        "半兽人 (Half-Orc)": """
            Half-Orcs blend human and orcish features:
            - Grayish or greenish skin tones
            - Jutting lower canines (tusks)
            - Slightly pointed ears
            - Heavy brow ridge and receding hairline
            - Strong jawline
            - Muscular, imposing physique
            - Often have facial scars
            - Coarse dark hair
        """,

        "半精灵 (Half-Elf)": """
            Half-Elves combine elven and human traits:
            - Slightly pointed ears (less pronounced than full elves)
            - More refined facial features than humans but less angular than elves
            - Eyes may have unusual colors
            - More slender than humans but more robust than elves
            - Smooth skin with subtle features
            - Various skin tones depending on parentage
        """,

        "侏儒 (Gnome)": """
            Gnomes are small beings with distinctive features:
            - Very small stature (3-4 feet tall)
            - Large heads relative to their bodies
            - Pointed or slightly pointed ears
            - Bright, expressive eyes often with unusual colors
            - Wide smiles
            - Often have large noses
            - Males typically have impressive facial hair
            - Animated facial expressions
        """,

        "半身人 (Halfling)": """
            Halflings are small with distinctive traits:
            - Very small stature (about 3 feet tall)
            - Proportions like small adults, not children
            - Round faces with rosy cheeks
            - Large, dexterous hands and feet
            - Often barefoot with hairy tops of feet
            - Curly hair (usually brown or black)
            - Warm, friendly expressions
            - Nimble appearance
        """,

        "矮人 (Dwarf)": """
            Dwarves are stout, sturdy beings:
            - Short, stocky build (4-5 feet tall but broad)
            - Very robust physique with notable muscle
            - Long beards for males (often braided or decorated)
            - Earth-tone skin from pale to deep brown
            - Broad noses and bushy eyebrows
            - Deep-set eyes
            - Practical clothing with geometric patterns
            - Thick, strong hands
        """,

        "精灵 (Elf)": """
            Elves are graceful beings with ethereal beauty:
            - Slender, graceful build
            - Distinctly pointed ears
            - Angular, symmetrical facial features
            - Almond-shaped eyes that may have unusual colors
            - No facial hair
            - Typically taller than humans but more slender
            - Ageless appearance
            - Smooth skin without blemishes
            - Elegant posture
            - Long, typically straight hair
        """,

        "人类 (Human)": """
            Humans in D&D show great diversity:
            - Variable appearance
            - Round ears
            - Standard human proportions
            - Diverse skin tones, facial features, and body types
            - Wide range of hairstyles
            - Facial hair common for males
            - Clothing varies by region and culture
            - Most adaptable appearance of any race
        """
    }

    # 获取基本种族描述
    base_description = race_appearance.get(
        race, "A fantasy character with distinct racial features.")

    # 添加亚种特征描述（如果有）
    subrace_details = ""
    if subrace:
        if race == "精灵 (Elf)":
            if subrace == "高等精灵":
                subrace_details = "High Elves typically have fair skin, hair in shades of blonde or black, and blue, green, or gold eyes."
            elif subrace == "木精灵":
                subrace_details = "Wood Elves typically have copper-colored skin with hints of green, brown or black hair, and green, brown, or hazel eyes."
            elif subrace == "黑暗精灵":
                subrace_details = "Drow have obsidian, charcoal, or dark blue skin, white or pale yellow hair, and red, lavender, or blue eyes that glow in dim light."
        elif race == "矮人 (Dwarf)":
            if subrace == "山地矮人":
                subrace_details = "Mountain Dwarves are lighter skinned than Hill Dwarves, with more ruddy complexions and lighter hair."
            elif subrace == "丘陵矮人":
                subrace_details = "Hill Dwarves have deep tan or light brown skin, with brown or black hair, and brown or hazel eyes."
        elif race == "龙裔 (Dragonborn)":
            dragon_colors = {
                "黑龙": "Black-scaled with acid resistance",
                "蓝龙": "Blue-scaled with lightning resistance",
                "绿龙": "Green-scaled with poison resistance",
                "红龙": "Red-scaled with fire resistance",
                "白龙": "White-scaled with cold resistance",
                "金龙": "Gold-scaled with fire resistance",
                "银龙": "Silver-scaled with cold resistance",
                "铜龙": "Copper-scaled with acid resistance",
                "青铜龙": "Bronze-scaled with lightning resistance",
                "黄铜龙": "Brass-scaled with fire resistance",
            }
            subrace_details = dragon_colors.get(subrace, "")

    return f"{base_description}\n{subrace_details}".strip()


def get_class_appearance_details(character_class):
    """获取D&D职业的视觉特征描述，确保图像生成准确反映职业特征"""

    class_appearance = {
        "战士 (Fighter)": """
            Fighter visual elements include:
            - Well-maintained armor appropriate to their fighting style
            - Multiple visible weapons showing their combat versatility
            - Battle scars or callused hands showing experience
            - Alert, tactical expression and stance
            - Practical, serviceable equipment with minimal decoration
            - Possibly a shield or defensive items
            - Strong, trained physique
        """,

        "法师 (Wizard)": """
            Wizard visual elements include:
            - Robes or clothing with arcane symbols or runes
            - Spell component pouch or focus item (orb, wand, staff)
            - Book, scroll or other written materials
            - Minimal or no physical armor
            - Perhaps a familiar or magical trinket
            - Thoughtful, studious expression
            - Possibly glowing eyes or magical effects
        """,

        "游荡者 (Rogue)": """
            Rogue visual elements include:
            - Light, flexible clothing allowing easy movement
            - Multiple visible or partially concealed daggers/weapons
            - Hooded or shadowed face
            - Lockpicks, thieves' tools, or other specialized equipment
            - Leather armor or protective gear that doesn't restrict movement
            - Alert, observant expression with calculating eyes
            - Possibly trinkets or trophies from past exploits
        """,

        "牧师 (Cleric)": """
            Cleric visual elements include:
            - Religious symbol prominently displayed
            - Ceremonial clothing or armor showing their faith
            - Holy book, scroll or prayer beads
            - Divine focus or implement
            - Expression of piety, wisdom or conviction
            - Possibly glowing hands or divine aura
            - Clothing colors matching their deity's symbolism
        """,

        "野蛮人 (Barbarian)": """
            Barbarian visual elements include:
            - Minimal armor, showing their reliance on natural toughness
            - Tribal markings, tattoos, or war paint
            - Large, intimidating weapons
            - Trophies from defeated enemies (teeth, claws, skulls)
            - Wild, untamed appearance
            - Intense, fierce expression
            - Muscular, powerful physique
        """,

        "吟游诗人 (Bard)": """
            Bard visual elements include:
            - Musical instrument (lute, flute, drums)
            - Flamboyant, colorful clothing with fine details
            - Charming expression or charismatic smile
            - Trinkets or tokens from various cultures
            - Light, practical armor if any
            - Possibly a magical focus disguised as jewelry
            - Elegant or expressive posture
        """,

        "德鲁伊 (Druid)": """
            Druid visual elements include:
            - Natural materials (leather, wood, leaves, vines)
            - Animal companions or natural creatures nearby
            - Staff, sickle, or natural focus item
            - Clothing adorned with natural elements
            - Tribal tattoos or body paint with nature symbolism
            - Calm, observant expression
            - No metal armor or minimal metal items
        """,

        "武僧 (Monk)": """
            Monk visual elements include:
            - Simple, functional clothing allowing full movement
            - Minimal or no armor
            - Disciplined posture and controlled expression
            - Possibly shaved head or simple hairstyle
            - Ritual scarification or tattoos for some traditions
            - Focused, meditative expression
            - Possibly prayer beads or spiritual focus items
        """,

        "圣武士 (Paladin)": """
            Paladin visual elements include:
            - Gleaming, well-maintained armor
            - Holy symbol prominently displayed
            - Righteous expression of purpose
            - Weapon or shield with religious iconography
            - Aura of authority and conviction
            - Clean, orderly appearance
            - Colors and emblems of their oath or order
        """,

        "游侠 (Ranger)": """
            Ranger visual elements include:
            - Practical, weathered clothing in earth tones
            - Bow, quiver, or hunting weapons
            - Camouflage elements or forest colors
            - Animal companion or tracking tools
            - Alert, watchful expression
            - Wilderness survival gear
            - Light or medium armor allowing mobility
        """,

        "术士 (Sorcerer)": """
            Sorcerer visual elements include:
            - Distinctive features hinting at their magical bloodline
            - Clothing with elements matching their magic source
            - Minimal physical armor or protection
            - Confident expression of innate power
            - Possibly glowing eyes or magical manifestations
            - Arcane focus item (orb, crystal, rod)
            - Dynamic, energetic presence
        """,

        "邪术师 (Warlock)": """
            Warlock visual elements include:
            - Eldritch symbols or patron's iconography
            - Otherworldly features from their pact
            - Mysterious, arcane accessories
            - Unusual eyes reflecting their patron
            - Dark or distinctive clothing
            - Possibly a familiar or pact weapon
            - Unsettling or commanding presence
            - Eldritch focus or strange trinkets
        """
    }

    return class_appearance.get(character_class, "A character with distinctive features representing their profession and training.")


@api_view(["DELETE"])
def delete_image(request, public_id):
    """
    从Cloudinary删除指定的图片
    """
    try:
        result = delete_cloudinary_image(public_id)

        if result['success']:
            return Response({
                "message": f"图片 {public_id} 已成功删除"
            }, status=200)
        else:
            return Response({
                "error": f"删除图片失败: {result.get('error')}"
            }, status=400)

    except Exception as e:
        return Response({"error": f"删除图片时出错: {str(e)}"}, status=500)
