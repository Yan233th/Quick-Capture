import os
import queue
import time
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()

PROXY_ENABLED = os.getenv("PROXY_ENABLED", "false").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL")

if PROXY_ENABLED and PROXY_URL:
    os.environ["HTTP_PROXY"] = PROXY_URL
    os.environ["HTTPS_PROXY"] = PROXY_URL
    print(f"Proxy enabled and set to: {PROXY_URL}")
elif PROXY_ENABLED and not PROXY_URL:
    print("Warning: PROXY_ENABLED is true, but no PROXY_URL is set.")

API_KEY = os.getenv("GOOGLE_API_KEY")
THINKING_BUDGET = int(os.getenv("THINKING_BUDGET", "0"))

MODEL_NAME = "gemini-flash-latest"
DEFAULT_PROMPT = "Respond appropriately based on what you see. For example, if it's a question, answer it."

client = None
if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        print(f"Error initializing AI client: {e}")


def image2part(image: Image.Image) -> types.Part:
    buf = BytesIO()
    image.save(buf, format="png")
    return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")


def send_to_ai_stream(image: Image.Image, q: queue.Queue):
    print("Streaming image to AI for analysis...")
    if not client:
        mock_response = f"AI model not configured. Mock response.\nImage size: {image.width}x{image.height}"
        for char in mock_response:
            q.put(char)
            time.sleep(0.05)
        q.put(None)
        return

    try:
        contents = [
            types.Content(role="user", parts=[types.Part.from_text(text=DEFAULT_PROMPT), image2part(image)]),
        ]
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=THINKING_BUDGET,
            ),
        )
        response = client.models.generate_content_stream(model=MODEL_NAME, contents=contents, config=config)

        for chunk in response:
            q.put(chunk.text)
        q.put(None)
    except Exception as e:
        error_message = f"Error during AI call: {e}"
        print(error_message)
        q.put(error_message)
        q.put(None)
