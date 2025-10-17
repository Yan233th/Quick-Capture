import os
import queue
import time
from PIL import Image

PROXY_ENABLED = os.getenv("PROXY_ENABLED", "false").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL")

if PROXY_ENABLED and PROXY_URL:
    os.environ["HTTP_PROXY"] = PROXY_URL
    os.environ["HTTPS_PROXY"] = PROXY_URL
    print(f"Proxy enabled and set to: {PROXY_URL}")
elif PROXY_ENABLED and not PROXY_URL:
    print("Warning: PROXY_ENABLED is true, but no PROXY_URL is set in .env file. Proxy will not be used.")

API_KEY = os.getenv("GOOGLE_API_KEY")
THINKING_BUDGET = int(os.getenv("THINKING_BUDGET", "0"))

client = None
if API_KEY:
    try:
        from google import generativeai
        from google.generativeai import types

        client = generativeai.Client(api_key=API_KEY)
    except ImportError:
        print("Warning: 'google-generativeai' is not installed. AI functionality will be disabled.")
    except Exception as e:
        print(f"Error initializing AI client: {e}")


def send_to_ai_stream(image: Image.Image, q: queue.Queue):
    print("Streaming image to AI for analysis...")
    if not client:
        mock_response = f"AI model not configured. This is a mock response.\nImage size: {image.width}x{image.height}"
        for char in mock_response:
            q.put(char)
            time.sleep(0.05)
        q.put(None)
        return

    try:
        model_name = "gemini-flash-latest"
        contents = [
            types.Content(
                role="user",
                parts=["Respond appropriately based on what you see. For example, if it's a question, answer it.", image],
            ),
        ]
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=THINKING_BUDGET,
            ),
        )

        response = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )

        for chunk in response:
            q.put(chunk.text)
        q.put(None)

    except Exception as e:
        error_message = f"Error during AI call: {e}"
        print(error_message)
        q.put(error_message)
        q.put(None)
