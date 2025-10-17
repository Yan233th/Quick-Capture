import os
import queue
import time
from PIL import Image

# --- Proxy Configuration Loading ---
PROXY_ENABLED = os.getenv("PROXY_ENABLED", "false").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL")

if PROXY_ENABLED and PROXY_URL:
    os.environ["HTTP_PROXY"] = PROXY_URL
    os.environ["HTTPS_PROXY"] = PROXY_URL
    print(f"Proxy enabled and set to: {PROXY_URL}")
elif PROXY_ENABLED and not PROXY_URL:
    print("Warning: PROXY_ENABLED is true, but no PROXY_URL is set in .env file. Proxy will not be used.")

# --- AI Model Initialization ---
API_KEY = os.getenv("GOOGLE_API_KEY")

model = None
if API_KEY:
    try:
        import google.generativeai as genai

        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
    except ImportError:
        print("Warning: 'google-generativeai' is not installed. AI functionality will be disabled.")
    except Exception as e:
        print(f"Error initializing AI model: {e}")


def send_to_ai_stream(image: Image.Image, q: queue.Queue):
    print("Streaming image to AI for analysis...")
    if not model:
        mock_response = f"AI model not configured. This is a mock response.\nImage size: {image.width}x{image.height}"
        for char in mock_response:
            q.put(char)
            time.sleep(0.05)
        q.put(None)
        return

    try:
        response = model.generate_content(["Describe what you see in this image.", image], stream=True)
        for chunk in response:
            q.put(chunk.text)
        q.put(None)
    except Exception as e:
        error_message = f"Error during AI call: {e}"
        print(error_message)
        q.put(error_message)
        q.put(None)
