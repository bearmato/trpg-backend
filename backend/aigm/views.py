
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
    """Generate character background story based on keywords"""

    # Get character information
    character_name = request.data.get("name", "")
    character_race = request.data.get("race", "")
    character_class = request.data.get("class", "")
    keywords = request.data.get("keywords", [])
    tone = request.data.get("tone", "balanced")  # Default tone

    if not character_name or not character_race or not character_class:
        return Response({"error": "Character name, race, and class are required"}, status=400)

    try:
        # Build prompt for character background
        keywords_text = ", ".join(keywords) if keywords else "none specified"
        background_prompt = f"""Create a compelling background story for a TRPG character with the following details:
        
        - Name: {character_name}
        - Race: {character_race}
        - Class: {character_class}
        - Tone/Theme: {tone}
        - Key elements to include: {keywords_text}
        
        The background should explain their origin, motivation, how they acquired their abilities, 
        and perhaps a significant event that shaped them. Keep it concise (3-5 paragraphs) but rich 
        in character development. Make sure the story aligns with classic TRPG lore while being unique.
        """

        # Send message to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert storyteller specializing in creating character backgrounds for tabletop RPGs."},
                {"role": "user", "content": background_prompt}
            ],
            temperature=0.8,  # Creative enough for unique stories
            max_tokens=800,
            top_p=1,
            frequency_penalty=0.3,  # Reduce repetition
            presence_penalty=0.3
        )

        # Get AI response
        background_story = response.choices[0].message.content

        return Response({
            "background": background_story,
            "name": character_name,
            "race": character_race,
            "class": character_class
        }, status=200)

    except Exception as e:
        return Response({"error": f"Error generating character background: {str(e)}"}, status=500)
